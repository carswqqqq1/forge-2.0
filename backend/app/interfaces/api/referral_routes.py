from datetime import UTC, datetime
import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.domain.models.user import User
from app.infrastructure.models.documents import ReferralDocument, UsageLedgerDocument, UserDocument
from app.interfaces.dependencies import get_current_user
from app.interfaces.schemas.base import APIResponse

router = APIRouter(prefix="/referrals", tags=["referrals"])


class ReferralResponse(BaseModel):
    invite_link: str
    referral_code: str
    credits_earned: int
    referral_count: int


class RedeemReferralRequest(BaseModel):
    code: str


async def _get_or_create_referral(user_id: str) -> ReferralDocument:
    existing = await ReferralDocument.find_one(ReferralDocument.user_id == user_id)
    if existing:
        return existing
    code = uuid.uuid4().hex[:8]
    doc = ReferralDocument(
        referral_id=uuid.uuid4().hex[:16],
        user_id=user_id,
        referral_code=code,
        invite_link=f"https://forge-2-0-fsvibxs.netlify.app/?ref={code}",
    )
    await doc.insert()
    return doc


@router.get("/my-link", response_model=APIResponse[ReferralResponse])
async def get_my_link(current_user: User = Depends(get_current_user)) -> APIResponse[ReferralResponse]:
    doc = await _get_or_create_referral(current_user.id)
    return APIResponse.success(
        ReferralResponse(
            invite_link=doc.invite_link,
            referral_code=doc.referral_code,
            credits_earned=doc.credits_earned,
            referral_count=doc.referral_count,
        )
    )


@router.post("/redeem", response_model=APIResponse[ReferralResponse])
async def redeem_referral(
    request: RedeemReferralRequest,
    current_user: User = Depends(get_current_user),
) -> APIResponse[ReferralResponse]:
    doc = await ReferralDocument.find_one(ReferralDocument.referral_code == request.code)
    if not doc:
        raise HTTPException(status_code=404, detail="Referral code not found")
    if doc.user_id == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot redeem your own referral code")
    doc.referral_count += 1
    doc.credits_earned += 500
    await doc.save()

    user_doc = await UserDocument.find_one(UserDocument.user_id == current_user.id)
    if user_doc:
        user_doc.credits += 500
        user_doc.updated_at = datetime.now(UTC)
        await user_doc.save()

    await UsageLedgerDocument(
        ledger_id=uuid.uuid4().hex[:16],
        user_id=current_user.id,
        source_type="referral",
        label=f"Redeemed referral {request.code}",
        credits_delta=500,
    ).insert()
    return APIResponse.success(
        ReferralResponse(
            invite_link=doc.invite_link,
            referral_code=doc.referral_code,
            credits_earned=doc.credits_earned,
            referral_count=doc.referral_count,
        )
    )
