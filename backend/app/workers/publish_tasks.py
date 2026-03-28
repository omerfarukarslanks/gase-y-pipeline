"""Celery tasks for video publishing."""

import asyncio
import logging
import uuid
from datetime import datetime, timezone

from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


def _run_async(coro):
    """Run an async coroutine from a sync Celery task."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


async def _publish_video_pipeline(publish_job_id: str, task=None):
    """Full async publish pipeline."""
    from sqlalchemy import select

    from app.db.session import async_session_factory
    from app.models.platform_account import PlatformAccount
    from app.models.publish_job import PublishJob
    from app.models.video_variant import VideoVariant
    from app.services.publisher import PublishService

    async with async_session_factory() as db:
        # 1. Fetch publish job
        result = await db.execute(
            select(PublishJob).where(PublishJob.id == uuid.UUID(publish_job_id))
        )
        job = result.scalar_one_or_none()
        if not job:
            raise ValueError(f"PublishJob {publish_job_id} not found")

        # 2. Fetch video variant
        result = await db.execute(
            select(VideoVariant).where(VideoVariant.id == job.video_variant_id)
        )
        variant = result.scalar_one_or_none()
        if not variant or not variant.file_url:
            job.status = "failed"
            job.error_message = "Video variant not found or has no file"
            await db.commit()
            raise ValueError(f"VideoVariant {job.video_variant_id} not ready")

        # 3. Fetch platform account
        result = await db.execute(
            select(PlatformAccount).where(PlatformAccount.id == job.platform_account_id)
        )
        account = result.scalar_one_or_none()
        if not account or not account.is_active:
            job.status = "failed"
            job.error_message = "Platform account not found or inactive"
            await db.commit()
            raise ValueError(f"PlatformAccount {job.platform_account_id} not available")

        # Get user_id for notifications
        user_id = str(account.user_id)

        # Update status
        job.status = "publishing"
        await db.commit()

        from app.utils.notifications import notify_publish_status
        notify_publish_status(user_id, publish_job_id, "publishing")

        if task:
            task.update_state(
                state="PROCESSING",
                meta={"step": "uploading", "platform": job.platform},
            )

        try:
            # 4. Build credentials dict
            credentials = {
                "access_token": account.access_token,
                "refresh_token": account.refresh_token,
                "platform_user_id": account.platform_user_id,
            }

            # 5. Build publish params with metadata overrides
            meta = job.publish_metadata or {}
            title = meta.get("title_override") or variant.title or "Untitled Video"
            description = meta.get("description_override") or variant.description or ""
            tags = meta.get("tags_override") or variant.hashtags

            # Remove override keys from extra kwargs
            extra_kwargs = {
                k: v for k, v in meta.items()
                if k not in ("title_override", "description_override", "tags_override", "language")
            }

            publish_result = await PublishService.publish_video(
                platform=job.platform,
                credentials=credentials,
                video_path=variant.file_url,
                title=title,
                description=description,
                tags=tags,
                **extra_kwargs,
            )

            # 6. Update job with result
            job.platform_post_id = publish_result.get("platform_post_id")
            job.platform_url = publish_result.get("platform_url")
            job.published_at = datetime.now(timezone.utc)
            job.status = "published"
            await db.commit()

            notify_publish_status(user_id, publish_job_id, "published", platform_url=job.platform_url)
            logger.info(f"Published job {publish_job_id} to {job.platform}: {job.platform_url}")
            return {
                "publish_job_id": publish_job_id,
                "status": "published",
                "platform_url": job.platform_url,
            }

        except Exception as e:
            logger.error(f"Publishing failed for job {publish_job_id}: {e}")
            job.status = "failed"
            job.error_message = str(e)[:500]
            await db.commit()
            notify_publish_status(user_id, publish_job_id, "failed")
            raise


@celery_app.task(bind=True, name="publish_video", max_retries=3)
def publish_video_task(self, publish_job_id: str):
    """Publish a video to a social media platform."""
    logger.info(f"Starting publish for job_id={publish_job_id}")
    try:
        result = _run_async(_publish_video_pipeline(publish_job_id, task=self))
        return result
    except Exception as exc:
        logger.error(f"Publish task failed: {exc}")
        raise self.retry(exc=exc, countdown=60)


async def _check_scheduled_publishes():
    """Find and dispatch due scheduled publish jobs."""
    from sqlalchemy import select

    from app.db.session import async_session_factory
    from app.models.publish_job import PublishJob

    async with async_session_factory() as db:
        now = datetime.now(timezone.utc)
        result = await db.execute(
            select(PublishJob).where(
                PublishJob.status == "scheduled",
                PublishJob.scheduled_at <= now,
            )
        )
        due_jobs = result.scalars().all()

        dispatched = 0
        for job in due_jobs:
            job.status = "pending"
            await db.commit()
            publish_video_task.delay(str(job.id))
            dispatched += 1

        logger.info(f"Dispatched {dispatched} scheduled publish jobs")
        return {"dispatched": dispatched}


@celery_app.task(name="scheduled_publish")
def scheduled_publish_task():
    """Check for and execute scheduled publish jobs. Run via Celery Beat."""
    logger.info("Checking for scheduled publish jobs...")
    return _run_async(_check_scheduled_publishes())
