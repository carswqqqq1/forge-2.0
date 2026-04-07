from datetime import UTC, datetime
import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.domain.models.user import User
from app.infrastructure.models.documents import ConnectorDocument
from app.interfaces.dependencies import get_current_user
from app.interfaces.schemas.base import APIResponse

router = APIRouter(prefix="/connectors", tags=["connectors"])

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


@router.get("", response_model=APIResponse[list[ConnectorResponse]])
async def list_connectors(current_user: User = Depends(get_current_user)) -> APIResponse[list[ConnectorResponse]]:
    connected = await ConnectorDocument.find(ConnectorDocument.user_id == current_user.id).to_list()
    connected_by_id = {item.connector_id: item for item in connected}
    items: list[ConnectorResponse] = []
    for connector in CONNECTOR_CATALOG:
        match = connected_by_id.get(connector["id"])
        items.append(
            ConnectorResponse(
                connector_id=connector["id"],
                name=connector["name"],
                description=connector["description"],
                type=connector["type"],
                status=match.status if match else "disconnected",
                connected_at=match.connected_at if match else None,
                metadata=match.metadata if match else {},
            )
        )
    return APIResponse.success(items)


@router.post("/{connector_id}/connect", response_model=APIResponse[ConnectorResponse])
async def connect_connector(
    connector_id: str,
    request: ConnectorConnectRequest,
    current_user: User = Depends(get_current_user),
) -> APIResponse[ConnectorResponse]:
    catalog_item = next((item for item in CONNECTOR_CATALOG if item["id"] == connector_id), None)
    if not catalog_item:
        raise HTTPException(status_code=404, detail="Connector not found")
    doc = await ConnectorDocument.find_one(ConnectorDocument.user_id == current_user.id, ConnectorDocument.connector_id == connector_id)
    if not doc:
        doc = ConnectorDocument(
            connection_id=uuid.uuid4().hex[:16],
            user_id=current_user.id,
            connector_id=connector_id,
            name=catalog_item["name"],
            type=request.type,
            auth_token=request.auth_token,
            metadata=request.metadata,
            status="connected",
        )
        await doc.insert()
    else:
        doc.auth_token = request.auth_token
        doc.metadata = request.metadata
        doc.status = "connected"
        doc.connected_at = datetime.now(UTC)
        await doc.save()
    return APIResponse.success(
        ConnectorResponse(
            connector_id=connector_id,
            name=catalog_item["name"],
            description=catalog_item["description"],
            type=doc.type,
            status=doc.status,
            connected_at=doc.connected_at,
            metadata=doc.metadata,
        )
    )


@router.delete("/{connector_id}", response_model=APIResponse[dict])
async def disconnect_connector(connector_id: str, current_user: User = Depends(get_current_user)) -> APIResponse[dict]:
    doc = await ConnectorDocument.find_one(ConnectorDocument.user_id == current_user.id, ConnectorDocument.connector_id == connector_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Connector not found")
    await doc.delete()
    return APIResponse.success({})
