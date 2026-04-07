from datetime import UTC, datetime, timedelta
import re
import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.domain.models.user import User
from app.infrastructure.models.documents import ScheduleDocument
from app.interfaces.dependencies import get_current_user
from app.interfaces.schemas.base import APIResponse

router = APIRouter(prefix="/schedules", tags=["schedules"])


class ScheduleRequest(BaseModel):
    name: str
    description: str = ""
    schedule_text: str
    status: str = "active"


class ScheduleResponse(BaseModel):
    schedule_id: str
    name: str
    description: str
    schedule_text: str
    cron_expression: str
    next_run: datetime | None
    status: str
    created_at: datetime
    updated_at: datetime


def _parse_schedule(schedule_text: str) -> tuple[str, datetime]:
    text = schedule_text.lower()
    now = datetime.now(UTC)
    hour = 9
    minute = 0
    time_match = re.search(r"(\d{1,2})(?::(\d{2}))?\s*(am|pm)?", text)
    if time_match:
        hour = int(time_match.group(1))
        minute = int(time_match.group(2) or 0)
        meridiem = time_match.group(3)
        if meridiem == "pm" and hour < 12:
            hour += 12
        if meridiem == "am" and hour == 12:
            hour = 0

    if "weekly" in text or "every monday" in text or "monday" in text:
        day_map = {"monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3, "friday": 4, "saturday": 5, "sunday": 6}
        target_day = next((value for key, value in day_map.items() if key in text), 0)
        days_ahead = (target_day - now.weekday()) % 7 or 7
        next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0) + timedelta(days=days_ahead)
        return f"{minute} {hour} * * {target_day}", next_run
    if "monthly" in text:
        next_run = (now.replace(day=1, hour=hour, minute=minute, second=0, microsecond=0) + timedelta(days=32)).replace(day=1)
        return f"{minute} {hour} 1 * *", next_run
    next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if next_run <= now:
        next_run += timedelta(days=1)
    return f"{minute} {hour} * * *", next_run


@router.get("", response_model=APIResponse[list[ScheduleResponse]])
async def list_schedules(current_user: User = Depends(get_current_user)) -> APIResponse[list[ScheduleResponse]]:
    items = await ScheduleDocument.find(ScheduleDocument.user_id == current_user.id).sort("-updated_at").to_list()
    return APIResponse.success([ScheduleResponse(**item.model_dump()) for item in items])


@router.post("", response_model=APIResponse[ScheduleResponse])
async def create_schedule(
    request: ScheduleRequest,
    current_user: User = Depends(get_current_user),
) -> APIResponse[ScheduleResponse]:
    cron_expression, next_run = _parse_schedule(request.schedule_text)
    doc = ScheduleDocument(
        schedule_id=uuid.uuid4().hex[:16],
        user_id=current_user.id,
        name=request.name or "New schedule",
        description=request.description,
        schedule_text=request.schedule_text,
        cron_expression=cron_expression,
        next_run=next_run,
        status=request.status,
    )
    await doc.insert()
    return APIResponse.success(ScheduleResponse(**doc.model_dump()))


@router.patch("/{schedule_id}", response_model=APIResponse[ScheduleResponse])
async def update_schedule(
    schedule_id: str,
    request: ScheduleRequest,
    current_user: User = Depends(get_current_user),
) -> APIResponse[ScheduleResponse]:
    doc = await ScheduleDocument.find_one(ScheduleDocument.schedule_id == schedule_id, ScheduleDocument.user_id == current_user.id)
    if not doc:
        raise HTTPException(status_code=404, detail="Schedule not found")
    cron_expression, next_run = _parse_schedule(request.schedule_text)
    doc.name = request.name or doc.name
    doc.description = request.description
    doc.schedule_text = request.schedule_text
    doc.cron_expression = cron_expression
    doc.next_run = next_run
    doc.status = request.status
    doc.updated_at = datetime.now(UTC)
    await doc.save()
    return APIResponse.success(ScheduleResponse(**doc.model_dump()))


@router.delete("/{schedule_id}", response_model=APIResponse[dict])
async def delete_schedule(schedule_id: str, current_user: User = Depends(get_current_user)) -> APIResponse[dict]:
    doc = await ScheduleDocument.find_one(ScheduleDocument.schedule_id == schedule_id, ScheduleDocument.user_id == current_user.id)
    if not doc:
        raise HTTPException(status_code=404, detail="Schedule not found")
    await doc.delete()
    return APIResponse.success({})
