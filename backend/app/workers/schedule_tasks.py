"""Celery tasks for scheduling, analytics collection, and token refresh."""

import asyncio
import logging
from datetime import datetime, timedelta, timezone

from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


def _run_async(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


async def _collect_analytics():
    """Collect latest analytics for all published jobs."""
    from sqlalchemy import select

    from app.db.session import async_session_factory
    from app.models.analytics import AnalyticsSnapshot
    from app.models.platform_account import PlatformAccount
    from app.models.publish_job import PublishJob

    async with async_session_factory() as db:
        # Get all published jobs
        result = await db.execute(
            select(PublishJob, PlatformAccount)
            .join(PlatformAccount, PublishJob.platform_account_id == PlatformAccount.id)
            .where(PublishJob.status == "published")
        )
        rows = result.all()
        collected = 0

        for job, account in rows:
            try:
                # Fetch metrics from platform API
                metrics = await _fetch_platform_metrics(
                    job.platform,
                    job.platform_post_id,
                    account,
                )
                if metrics:
                    snapshot = AnalyticsSnapshot(
                        publish_job_id=job.id,
                        views=metrics.get("views", 0),
                        likes=metrics.get("likes", 0),
                        comments=metrics.get("comments", 0),
                        shares=metrics.get("shares", 0),
                        watch_time_sec=metrics.get("watch_time_sec"),
                    )
                    db.add(snapshot)
                    collected += 1
            except Exception as e:
                logger.warning(f"Failed to collect analytics for job {job.id}: {e}")

        await db.commit()
        logger.info(f"Collected analytics for {collected}/{len(rows)} jobs")
        return {"collected": collected, "total": len(rows)}


async def _fetch_platform_metrics(
    platform: str,
    post_id: str | None,
    account,
) -> dict | None:
    """Fetch metrics from a platform API.

    Returns dict with views, likes, comments, shares, watch_time_sec.
    Returns None if metrics cannot be fetched.
    """
    if not post_id:
        return None

    import httpx

    if platform == "youtube" and account.access_token:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "https://www.googleapis.com/youtube/v3/videos",
                params={
                    "part": "statistics",
                    "id": post_id,
                },
                headers={"Authorization": f"Bearer {account.access_token}"},
            )
            if resp.status_code == 200:
                data = resp.json()
                items = data.get("items", [])
                if items:
                    stats = items[0].get("statistics", {})
                    return {
                        "views": int(stats.get("viewCount", 0)),
                        "likes": int(stats.get("likeCount", 0)),
                        "comments": int(stats.get("commentCount", 0)),
                        "shares": 0,
                    }

    elif platform == "instagram" and account.access_token:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"https://graph.instagram.com/{post_id}/insights",
                params={
                    "metric": "impressions,reach,likes,comments,shares",
                    "access_token": account.access_token,
                },
            )
            if resp.status_code == 200:
                data = resp.json().get("data", [])
                metrics = {}
                for item in data:
                    name = item.get("name", "")
                    value = item.get("values", [{}])[0].get("value", 0)
                    if name == "impressions":
                        metrics["views"] = value
                    elif name == "likes":
                        metrics["likes"] = value
                    elif name == "comments":
                        metrics["comments"] = value
                    elif name == "shares":
                        metrics["shares"] = value
                return metrics if metrics else None

    # For other platforms, return None (metrics collection not yet implemented)
    return None


async def _refresh_expiring_tokens():
    """Refresh OAuth tokens that are expiring soon."""
    from sqlalchemy import select

    from app.db.session import async_session_factory
    from app.models.platform_account import PlatformAccount

    threshold = datetime.now(timezone.utc) + timedelta(hours=1)

    async with async_session_factory() as db:
        result = await db.execute(
            select(PlatformAccount).where(
                PlatformAccount.is_active == True,
                PlatformAccount.token_expires_at.isnot(None),
                PlatformAccount.token_expires_at < threshold,
                PlatformAccount.refresh_token.isnot(None),
            )
        )
        accounts = result.scalars().all()
        refreshed = 0

        for account in accounts:
            try:
                new_tokens = await _refresh_token(account)
                if new_tokens:
                    account.access_token = new_tokens["access_token"]
                    if "refresh_token" in new_tokens:
                        account.refresh_token = new_tokens["refresh_token"]
                    if "expires_in" in new_tokens:
                        account.token_expires_at = datetime.now(timezone.utc) + timedelta(
                            seconds=new_tokens["expires_in"]
                        )
                    refreshed += 1
            except Exception as e:
                logger.error(f"Token refresh failed for {account.platform} ({account.id}): {e}")

        await db.commit()
        logger.info(f"Refreshed {refreshed}/{len(accounts)} tokens")
        return {"refreshed": refreshed, "total": len(accounts)}


async def _refresh_token(account) -> dict | None:
    """Refresh OAuth token for a platform account."""
    import httpx
    from app.config import settings

    token_urls = {
        "youtube": "https://oauth2.googleapis.com/token",
        "instagram": "https://graph.instagram.com/refresh_access_token",
        "twitter": "https://api.twitter.com/2/oauth2/token",
        "reddit": "https://www.reddit.com/api/v1/access_token",
        "tiktok": "https://open.tiktokapis.com/v2/oauth/token/",
    }

    url = token_urls.get(account.platform)
    if not url:
        return None

    async with httpx.AsyncClient() as client:
        if account.platform == "youtube":
            resp = await client.post(url, data={
                "grant_type": "refresh_token",
                "refresh_token": account.refresh_token,
                "client_id": settings.YOUTUBE_CLIENT_ID,
                "client_secret": settings.YOUTUBE_CLIENT_SECRET,
            })
        elif account.platform == "reddit":
            resp = await client.post(
                url,
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": account.refresh_token,
                },
                auth=(settings.REDDIT_CLIENT_ID, settings.REDDIT_CLIENT_SECRET),
            )
        else:
            # Generic OAuth2 refresh
            resp = await client.post(url, data={
                "grant_type": "refresh_token",
                "refresh_token": account.refresh_token,
            })

        if resp.status_code == 200:
            return resp.json()

    return None


@celery_app.task(name="collect_analytics")
def collect_analytics_task():
    """Periodically collect analytics from all connected platforms."""
    logger.info("Collecting analytics from platforms...")
    return _run_async(_collect_analytics())


@celery_app.task(name="refresh_tokens")
def refresh_tokens_task():
    """Refresh expiring OAuth tokens for platform accounts."""
    logger.info("Refreshing expiring tokens...")
    return _run_async(_refresh_expiring_tokens())
