from datetime import UTC, datetime
import secrets
import uuid
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field

from app.core.config import get_settings
from app.domain.models.user import User
from app.infrastructure.external.cache import get_cache
from app.infrastructure.models.documents import ConnectorDocument
from app.interfaces.dependencies import get_current_user
from app.interfaces.schemas.base import APIResponse

router = APIRouter(prefix="/connectors", tags=["connectors"])

GITHUB_SCOPES = "repo user read:org"
OAUTH_STATE_TTL_SECONDS = 600

CONNECTOR_CATALOG = [
    {"id": "my-browser", "name": "My Browser", "description": "Live browser context for Forge runs.", "type": "app"},
    {"id": "gmail", "name": "Gmail", "description": "Read and draft email from Forge.", "type": "app"},
    {"id": "google-calendar", "name": "Google Calendar", "description": "Scheduling and calendar access.", "type": "app"},
    {"id": "google-drive", "name": "Google Drive", "description": "Drive, Docs, Sheets, and Slides.", "type": "app"},
    {"id": "outlook-mail", "name": "Outlook Mail", "description": "Email access for Microsoft accounts.", "type": "app"},
    {"id": "outlook-calendar", "name": "Outlook Calendar", "description": "Calendar access for Microsoft accounts.", "type": "app"},
    {"id": "github", "name": "GitHub", "description": "Repos, PRs, issues, and code shipping.", "type": "app"},
    {"id": "instagram", "name": "Instagram", "description": "Social publishing workflows.", "type": "app"},
    {"id": "meta-ads-manager", "name": "Meta Ads Manager", "description": "Campaign analysis and reporting.", "type": "app"},
    {"id": "slack", "name": "Slack", "description": "Read and send Slack messages.", "type": "app"},
    {"id": "notion", "name": "Notion", "description": "Workspace notes and docs.", "type": "app"},
    {"id": "zapier", "name": "Zapier", "description": "Automated app workflows.", "type": "app"},
    {"id": "asana", "name": "Asana", "description": "Project and task management.", "type": "app"},
    {"id": "monday", "name": "monday.com", "description": "Work management boards.", "type": "app"},
    {"id": "make", "name": "Make", "description": "Automation scenarios and orchestration.", "type": "app"},
    {"id": "linear", "name": "Linear", "description": "Issue tracking for product teams.", "type": "app"},
    {"id": "atlassian", "name": "Atlassian", "description": "Jira and Confluence workflows.", "type": "app"},
    {"id": "clickup", "name": "ClickUp", "description": "Tasks and docs in one workspace.", "type": "app"},
    {"id": "supabase", "name": "Supabase", "description": "Database and auth access.", "type": "app"},
    {"id": "vercel", "name": "Vercel", "description": "Deploy and preview web apps.", "type": "app"},
    {"id": "neon", "name": "Neon", "description": "Serverless Postgres workflows.", "type": "app"},
    {"id": "prisma-postgres", "name": "Prisma Postgres", "description": "Database workflows for Prisma.", "type": "app"},
    {"id": "sentry", "name": "Sentry", "description": "Error monitoring and triage.", "type": "app"},
    {"id": "hugging-face", "name": "Hugging Face", "description": "Models, datasets, and spaces.", "type": "app"},
    {"id": "hubspot", "name": "HubSpot", "description": "CRM and marketing workflows.", "type": "app"},
    {"id": "intercom", "name": "Intercom", "description": "Customer support workflows.", "type": "app"},
    {"id": "stripe", "name": "Stripe", "description": "Billing and payments.", "type": "app"},
    {"id": "paypal-business", "name": "PayPal for Business", "description": "PayPal business operations.", "type": "app"},
    {"id": "revenuecat", "name": "RevenueCat", "description": "App subscription analytics.", "type": "app"},
    {"id": "close", "name": "Close", "description": "Sales CRM workflows.", "type": "app"},
    {"id": "xero", "name": "Xero", "description": "Accounting data and reports.", "type": "app"},
    {"id": "airtable", "name": "Airtable", "description": "Connected data and workflows.", "type": "app"},
    {"id": "google-drive-file-picker", "name": "Google Drive File Picker", "description": "Pick files from Drive into Forge.", "type": "app"},
    {"id": "custom-api", "name": "Custom API", "description": "Connect any HTTP API to Forge.", "type": "custom_api"},
    {"id": "custom-mcp", "name": "Custom MCP", "description": "Connect a custom MCP server.", "type": "custom_mcp"},
]

NON_INTERACTIVE_CONNECTORS = {"my-browser", "custom-api", "custom-mcp"}
MOCK_OAUTH_CONNECTORS = {
    item["id"]
    for item in CONNECTOR_CATALOG
    if item["id"] not in NON_INTERACTIVE_CONNECTORS and item["id"] != "github"
}


class ConnectorConnectRequest(BaseModel):
    auth_token: str | None = None
    metadata: dict = Field(default_factory=dict)
    type: str = "app"


class ConnectorResponse(BaseModel):
    connector_id: str
    name: str
    description: str
    type: str
    status: str
    connected_at: datetime | None = None
    metadata: dict = Field(default_factory=dict)
    oauth_url: str | None = None


def _catalog_item(connector_id: str) -> dict:
    catalog_item = next((item for item in CONNECTOR_CATALOG if item["id"] == connector_id), None)
    if not catalog_item:
        raise HTTPException(status_code=404, detail="Connector not found")
    return catalog_item


async def _upsert_connector(
    user_id: str,
    connector_id: str,
    *,
    auth_token: str | None = None,
    metadata: dict | None = None,
    type_override: str | None = None,
    status: str = "connected",
) -> ConnectorDocument:
    catalog_item = _catalog_item(connector_id)
    doc = await ConnectorDocument.find_one(ConnectorDocument.user_id == user_id, ConnectorDocument.connector_id == connector_id)
    if not doc:
        doc = ConnectorDocument(
            connection_id=uuid.uuid4().hex[:16],
            user_id=user_id,
            connector_id=connector_id,
            name=catalog_item["name"],
            type=type_override or catalog_item["type"],
            auth_token=auth_token,
            metadata=metadata or {},
            status=status,
        )
        await doc.insert()
    else:
        doc.type = type_override or doc.type or catalog_item["type"]
        doc.auth_token = auth_token if auth_token is not None else doc.auth_token
        doc.metadata = metadata or doc.metadata
        doc.status = status
        doc.connected_at = datetime.now(UTC)
        await doc.save()
    return doc


def _to_response(connector_id: str, *, doc: ConnectorDocument | None = None, oauth_url: str | None = None) -> ConnectorResponse:
    catalog_item = _catalog_item(connector_id)
    return ConnectorResponse(
        connector_id=connector_id,
        name=catalog_item["name"],
        description=catalog_item["description"],
        type=(doc.type if doc else catalog_item["type"]),
        status=(doc.status if doc else "disconnected"),
        connected_at=(doc.connected_at if doc else None),
        metadata=(doc.metadata if doc else {}),
        oauth_url=oauth_url,
    )


def _build_callback_url(request: Request, connector_id: str) -> str:
    return f"{str(request.base_url).rstrip('/')}/api/v1/connectors/{connector_id}/callback"


def _build_frontend_redirect(origin: str | None, connector_id: str, success: bool, reason: str | None = None) -> str:
    settings = get_settings()
    base = (origin or settings.frontend_url or "http://localhost:5173").rstrip("/")
    query = {"connected": connector_id} if success else {"connector_error": connector_id}
    if reason:
        query["reason"] = reason
    return f"{base}/chat?{urlencode(query)}"


@router.get("", response_model=APIResponse[list[ConnectorResponse]])
async def list_connectors(current_user: User = Depends(get_current_user)) -> APIResponse[list[ConnectorResponse]]:
    connected = await ConnectorDocument.find(ConnectorDocument.user_id == current_user.id).to_list()
    connected_by_id = {item.connector_id: item for item in connected}
    return APIResponse.success([_to_response(item["id"], doc=connected_by_id.get(item["id"])) for item in CONNECTOR_CATALOG])


@router.post("/{connector_id}/connect", response_model=APIResponse[ConnectorResponse])
async def connect_connector(
    connector_id: str,
    request_body: ConnectorConnectRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
) -> APIResponse[ConnectorResponse]:
    catalog_item = _catalog_item(connector_id)
    settings = get_settings()

    if connector_id == "github":
        if not settings.github_client_id or not settings.github_client_secret:
            raise HTTPException(status_code=400, detail="GitHub OAuth is not configured on this Forge instance")
        state = secrets.token_urlsafe(24)
        await get_cache().set(
            f"connector_oauth_state:{state}",
            {
                "user_id": current_user.id,
                "connector_id": connector_id,
                "frontend_origin": request.headers.get("origin") or settings.frontend_url,
                "redirect_uri": _build_callback_url(request, connector_id),
            },
            ttl=OAUTH_STATE_TTL_SECONDS,
        )
        oauth_url = (
            "https://github.com/login/oauth/authorize?"
            + urlencode(
                {
                    "client_id": settings.github_client_id,
                    "redirect_uri": _build_callback_url(request, connector_id),
                    "scope": GITHUB_SCOPES,
                    "state": state,
                }
            )
        )
        return APIResponse.success(_to_response(connector_id, oauth_url=oauth_url))

    if connector_id in MOCK_OAUTH_CONNECTORS:
        state = secrets.token_urlsafe(24)
        await get_cache().set(
            f"connector_oauth_state:{state}",
            {
                "user_id": current_user.id,
                "connector_id": connector_id,
                "frontend_origin": request.headers.get("origin") or settings.frontend_url,
                "redirect_uri": _build_callback_url(request, connector_id),
            },
            ttl=OAUTH_STATE_TTL_SECONDS,
        )
        oauth_url = f"{_build_callback_url(request, connector_id)}?{urlencode({'state': state, 'code': f'mock_{connector_id}'})}"
        return APIResponse.success(_to_response(connector_id, oauth_url=oauth_url))

    metadata = {**request_body.metadata}
    doc = await _upsert_connector(
        current_user.id,
        connector_id,
        auth_token=request_body.auth_token,
        metadata=metadata,
        type_override=request_body.type or catalog_item["type"],
    )
    return APIResponse.success(_to_response(connector_id, doc=doc))


@router.get("/{connector_id}/callback")
async def oauth_callback(
    connector_id: str,
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
) -> RedirectResponse:
    settings = get_settings()
    if not state:
        return RedirectResponse(_build_frontend_redirect(settings.frontend_url, connector_id, False, "missing_state"))

    cached_state = await get_cache().get(f"connector_oauth_state:{state}")
    await get_cache().delete(f"connector_oauth_state:{state}")
    if not cached_state:
        return RedirectResponse(_build_frontend_redirect(settings.frontend_url, connector_id, False, "invalid_state"))

    frontend_redirect_base = cached_state.get("frontend_origin")
    user_id = cached_state.get("user_id")
    cached_connector_id = cached_state.get("connector_id")
    redirect_uri = cached_state.get("redirect_uri")
    if not user_id or cached_connector_id != connector_id:
        return RedirectResponse(_build_frontend_redirect(frontend_redirect_base, connector_id, False, "state_mismatch"))
    if error:
        return RedirectResponse(_build_frontend_redirect(frontend_redirect_base, connector_id, False, error))

    if connector_id != "github":
        doc = await _upsert_connector(
            user_id,
            connector_id,
            metadata={"connected_via": "mock_oauth_callback"},
        )
        return RedirectResponse(_build_frontend_redirect(frontend_redirect_base, connector_id, True))

    if not code:
        return RedirectResponse(_build_frontend_redirect(frontend_redirect_base, connector_id, False, "missing_code"))

    async with httpx.AsyncClient(timeout=20.0) as client:
        token_response = await client.post(
            "https://github.com/login/oauth/access_token",
            headers={"Accept": "application/json"},
            data={
                "client_id": settings.github_client_id,
                "client_secret": settings.github_client_secret,
                "code": code,
                "redirect_uri": redirect_uri,
            },
        )
        token_payload = token_response.json()
        access_token = token_payload.get("access_token")
        if not access_token:
            return RedirectResponse(_build_frontend_redirect(frontend_redirect_base, connector_id, False, "token_exchange_failed"))

        user_response = await client.get(
            "https://api.github.com/user",
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {access_token}",
                "X-GitHub-Api-Version": "2022-11-28",
            },
        )
        user_payload = user_response.json() if user_response.status_code < 400 else {}

    await _upsert_connector(
        user_id,
        "github",
        auth_token=access_token,
        metadata={
            "connected_via": "oauth",
            "login": user_payload.get("login"),
            "avatar_url": user_payload.get("avatar_url"),
            "html_url": user_payload.get("html_url"),
            "scopes": GITHUB_SCOPES,
        },
    )
    return RedirectResponse(_build_frontend_redirect(frontend_redirect_base, "github", True))


@router.delete("/{connector_id}", response_model=APIResponse[dict])
async def disconnect_connector(connector_id: str, current_user: User = Depends(get_current_user)) -> APIResponse[dict]:
    doc = await ConnectorDocument.find_one(ConnectorDocument.user_id == current_user.id, ConnectorDocument.connector_id == connector_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Connector not found")
    await doc.delete()
    return APIResponse.success({})
