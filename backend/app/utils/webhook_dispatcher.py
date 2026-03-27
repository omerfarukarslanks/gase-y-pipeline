"""Webhook event dispatcher - sends HTTP POST to registered webhook URLs."""

import hashlib
import hmac
import json
import logging

import httpx

logger = logging.getLogger(__name__)


async def dispatch_webhook_event(
    user_id: str,
    event: str,
    payload: dict,
):
    """Dispatch a webhook event to all registered endpoints for a user.

    Args:
        user_id: User ID to look up webhooks for
        event: Event type (e.g. "video.completed")
        payload: Event payload data
    """
    from sqlalchemy import select
    from app.db.session import async_session_factory
    from app.models.webhook import Webhook

    async with async_session_factory() as db:
        result = await db.execute(
            select(Webhook).where(
                Webhook.user_id == user_id,
                Webhook.is_active == True,
            )
        )
        webhooks = result.scalars().all()

        for webhook in webhooks:
            if event not in webhook.events:
                continue

            body = json.dumps({
                "event": event,
                "payload": payload,
            })

            headers = {"Content-Type": "application/json"}
            if webhook.secret:
                signature = hmac.new(
                    webhook.secret.encode(),
                    body.encode(),
                    hashlib.sha256,
                ).hexdigest()
                headers["X-Webhook-Signature"] = f"sha256={signature}"

            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    resp = await client.post(
                        webhook.url, content=body, headers=headers
                    )
                    logger.info(
                        f"Webhook dispatched: {event} → {webhook.url} (status={resp.status_code})"
                    )
            except Exception as e:
                logger.error(f"Webhook dispatch failed: {event} → {webhook.url}: {e}")
