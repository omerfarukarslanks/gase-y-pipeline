"""Webhook registration and management API."""

import secrets
import uuid

from fastapi import APIRouter, Depends
from pydantic import BaseModel, HttpUrl
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.db.session import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.webhook import Webhook

router = APIRouter(prefix="/webhooks", tags=["webhooks"])

VALID_EVENTS = [
    "video.completed",
    "video.failed",
    "publish.completed",
    "publish.failed",
    "publish.scheduled",
]


class WebhookCreate(BaseModel):
    url: HttpUrl
    events: list[str]


class WebhookUpdate(BaseModel):
    url: HttpUrl | None = None
    events: list[str] | None = None
    is_active: bool | None = None


@router.get("/")
async def list_webhooks(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all registered webhooks."""
    result = await db.execute(
        select(Webhook)
        .where(Webhook.user_id == current_user.id)
        .order_by(Webhook.created_at.desc())
    )
    webhooks = result.scalars().all()
    return [
        {
            "id": str(w.id),
            "url": w.url,
            "events": w.events,
            "is_active": w.is_active,
            "created_at": w.created_at.isoformat(),
        }
        for w in webhooks
    ]


@router.get("/events")
async def list_available_events(
    current_user: User = Depends(get_current_user),
):
    """List available webhook event types."""
    return {"events": VALID_EVENTS}


@router.post("/")
async def register_webhook(
    data: WebhookCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Register a new webhook URL."""
    # Validate events
    invalid = [e for e in data.events if e not in VALID_EVENTS]
    if invalid:
        from app.core.exceptions import BadRequestException
        raise BadRequestException(f"Invalid events: {', '.join(invalid)}")

    webhook_secret = secrets.token_hex(32)

    webhook = Webhook(
        user_id=current_user.id,
        url=str(data.url),
        secret=webhook_secret,
        events=data.events,
        is_active=True,
    )
    db.add(webhook)
    await db.flush()

    return {
        "id": str(webhook.id),
        "url": webhook.url,
        "secret": webhook_secret,
        "events": webhook.events,
        "is_active": webhook.is_active,
    }


@router.put("/{webhook_id}")
async def update_webhook(
    webhook_id: uuid.UUID,
    data: WebhookUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a webhook."""
    result = await db.execute(
        select(Webhook).where(
            Webhook.id == webhook_id,
            Webhook.user_id == current_user.id,
        )
    )
    webhook = result.scalar_one_or_none()
    if not webhook:
        raise NotFoundException("Webhook not found")

    if data.url is not None:
        webhook.url = str(data.url)
    if data.events is not None:
        invalid = [e for e in data.events if e not in VALID_EVENTS]
        if invalid:
            from app.core.exceptions import BadRequestException
            raise BadRequestException(f"Invalid events: {', '.join(invalid)}")
        webhook.events = data.events
    if data.is_active is not None:
        webhook.is_active = data.is_active

    await db.flush()

    return {
        "id": str(webhook.id),
        "url": webhook.url,
        "events": webhook.events,
        "is_active": webhook.is_active,
    }


@router.delete("/{webhook_id}")
async def delete_webhook(
    webhook_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a webhook."""
    result = await db.execute(
        select(Webhook).where(
            Webhook.id == webhook_id,
            Webhook.user_id == current_user.id,
        )
    )
    webhook = result.scalar_one_or_none()
    if not webhook:
        raise NotFoundException("Webhook not found")

    await db.delete(webhook)
    return {"message": "Webhook deleted"}
