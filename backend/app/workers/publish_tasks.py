"""Celery tasks for video publishing."""

import logging

from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="publish_video")
def publish_video_task(self, publish_job_id: str):
    """Publish a video to a social media platform."""
    logger.info(f"Starting publish for job_id={publish_job_id}")

    # TODO: Implement
    # 1. Fetch publish_job, video_variant, platform_account from DB
    # 2. Create platform publisher via factory
    # 3. Upload video
    # 4. Update publish_job with platform_post_id and status

    return {"publish_job_id": publish_job_id, "status": "published"}


@celery_app.task(name="scheduled_publish")
def scheduled_publish_task():
    """Check for and execute scheduled publish jobs."""
    logger.info("Checking for scheduled publish jobs...")

    # TODO: Query publish_jobs where status=scheduled and scheduled_at <= now
    # Dispatch publish_video_task for each
