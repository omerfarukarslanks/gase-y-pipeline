"""
Notification utilities for sending real-time updates via Redis pub/sub.

Celery workers publish notifications to Redis channels.
The FastAPI app subscribes and forwards them to WebSocket clients.
"""

import json
import logging

import redis

from app.config import settings

logger = logging.getLogger(__name__)

# Redis client for publishing notifications
_redis_client = None


def _get_redis():
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.from_url(settings.REDIS_URL)
    return _redis_client


def notify_job_update(user_id: str, payload: dict):
    """
    Publish a job status update to Redis pub/sub.

    Called from Celery tasks to notify the FastAPI WebSocket handler.

    Args:
        user_id: The user who owns this job
        payload: Dict with job_id, status, step, progress, etc.
    """
    try:
        r = _get_redis()
        message = json.dumps({"user_id": user_id, **payload})
        r.publish("gasey:job_updates", message)
        logger.debug(f"Published notification for user {user_id}: {payload.get('status')}")
    except Exception as e:
        logger.warning(f"Failed to publish notification: {e}")


def notify_video_progress(user_id: str, video_id: str, step: str, status: str = "processing"):
    """Convenience method for video generation progress updates."""
    notify_job_update(user_id, {
        "type": "video_generation",
        "job_id": video_id,
        "step": step,
        "status": status,
    })


def notify_publish_status(user_id: str, publish_job_id: str, status: str, platform_url: str | None = None):
    """Convenience method for publish job status updates."""
    notify_job_update(user_id, {
        "type": "publish",
        "job_id": publish_job_id,
        "status": status,
        "platform_url": platform_url,
    })
