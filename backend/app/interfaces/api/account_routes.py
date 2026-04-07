from datetime import UTC, datetime, timedelta
from typing import Optional
import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.domain.models.user import User
from app.infrastructure.models.documents import BillingActivityDocument, UsageLedgerDocument, UserDocument
from app.interfaces.dependencies import get_current_user
from app.interfaces.schemas.base import APIResponse

router = APIRouter(prefix="/account", tags=["account"])


class AccountSummaryResponse(BaseModel):
    id: str
    fullname: str
    email: str
    nickname: str = ""
    occupation: str = ""
    more_about_you: str = ""
    custom_instructions: str = ""
    plan_name: str = "Forge Pro"
    plan_renewal_date: Optional[datetime] = None
    credits: int = 0
    free_credits: int = 0
    monthly_credits: int = 0
    monthly_credits_max: int = 0
    daily_refresh_credits: int = 0
    preferred_language: str = "English"
    appearance: str = "light"
    receive_product_updates: bool = True
    email_when_queued_task_starts: bool = True


class UsageItemResponse(BaseModel):
    id: str
    source_type: str
    label: str
    credits_delta: int
    created_at: datetime


class BillingItemResponse(BaseModel):
    id: str
    label: str
    amount: float
    currency: str
    created_at: datetime


class UpdateProfileRequest(BaseModel):
    nickname: str = ""
    occupation: str = ""
    more_about_you: str = ""
    custom_instructions: str = ""


class UpdateSettingsRequest(BaseModel):
    preferred_language: str = "English"
    appearance: str = "light"
    receive_product_updates: bool = True
    email_when_queued_task_starts: bool = True


async def _get_user_doc(user_id: str) -> UserDocument:
    doc = await UserDocument.find_one(UserDocument.user_id == user_id)
    if not doc:
        raise HTTPException(status_code=404, detail="User not found")
    if not doc.plan_renewal_date:
        doc.plan_renewal_date = datetime.now(UTC) + timedelta(days=30)
        await doc.save()
    return doc


def _to_summary(doc: UserDocument) -> AccountSummaryResponse:
    return AccountSummaryResponse(
        id=doc.user_id,
        fullname=doc.fullname,
        email=doc.email,
        nickname=doc.nickname,
        occupation=doc.occupation,
        more_about_you=doc.more_about_you,
        custom_instructions=doc.custom_instructions,
        plan_name=doc.plan_name,
        plan_renewal_date=doc.plan_renewal_date,
        credits=doc.credits,
        free_credits=doc.free_credits,
        monthly_credits=doc.monthly_credits,
        monthly_credits_max=doc.monthly_credits_max,
        daily_refresh_credits=doc.daily_refresh_credits,
        preferred_language=doc.preferred_language,
        appearance=doc.appearance,
        receive_product_updates=doc.receive_product_updates,
        email_when_queued_task_starts=doc.email_when_queued_task_starts,
    )


@router.get("/summary", response_model=APIResponse[AccountSummaryResponse])
async def get_account_summary(current_user: User = Depends(get_current_user)) -> APIResponse[AccountSummaryResponse]:
    doc = await _get_user_doc(current_user.id)
    return APIResponse.success(_to_summary(doc))


@router.patch("/profile", response_model=APIResponse[AccountSummaryResponse])
async def update_profile(
    request: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
) -> APIResponse[AccountSummaryResponse]:
    doc = await _get_user_doc(current_user.id)
    doc.nickname = request.nickname.strip()
    doc.occupation = request.occupation.strip()
    doc.more_about_you = request.more_about_you[:2000]
    doc.custom_instructions = request.custom_instructions[:3000]
    doc.updated_at = datetime.now(UTC)
    await doc.save()
    return APIResponse.success(_to_summary(doc))


@router.patch("/settings", response_model=APIResponse[AccountSummaryResponse])
async def update_settings(
    request: UpdateSettingsRequest,
    current_user: User = Depends(get_current_user),
) -> APIResponse[AccountSummaryResponse]:
    doc = await _get_user_doc(current_user.id)
    doc.preferred_language = request.preferred_language
    doc.appearance = request.appearance
    doc.receive_product_updates = request.receive_product_updates
    doc.email_when_queued_task_starts = request.email_when_queued_task_starts
    doc.updated_at = datetime.now(UTC)
    await doc.save()
    return APIResponse.success(_to_summary(doc))


@router.get("/usage", response_model=APIResponse[list[UsageItemResponse]])
async def get_usage(current_user: User = Depends(get_current_user)) -> APIResponse[list[UsageItemResponse]]:
    items = await UsageLedgerDocument.find(UsageLedgerDocument.user_id == current_user.id).sort("-created_at").limit(100).to_list()
    return APIResponse.success([
        UsageItemResponse(
            id=item.ledger_id,
            source_type=item.source_type,
            label=item.label,
            credits_delta=item.credits_delta,
            created_at=item.created_at,
        )
        for item in items
    ])


@router.get("/billing", response_model=APIResponse[list[BillingItemResponse]])
async def get_billing(current_user: User = Depends(get_current_user)) -> APIResponse[list[BillingItemResponse]]:
    items = await BillingActivityDocument.find(BillingActivityDocument.user_id == current_user.id).sort("-created_at").limit(50).to_list()
    if not items:
        seed = BillingActivityDocument(
            activity_id=uuid.uuid4().hex[:16],
            user_id=current_user.id,
            label="Forge Pro plan",
            amount=0,
            currency="USD",
        )
        await seed.insert()
        items = [seed]
    return APIResponse.success([
        BillingItemResponse(
            id=item.activity_id,
            label=item.label,
            amount=item.amount,
            currency=item.currency,
            created_at=item.created_at,
        )
        for item in items
    ])
