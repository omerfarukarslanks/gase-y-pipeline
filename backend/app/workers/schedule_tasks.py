"""Celery tasks for scheduling and analytics collection."""

import logging

from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="collect_analytics")
def collect_analytics_task():
    """Periodically collect analytics from all connected platforms."""
    logger.info("Collecting analytics from platforms...")

    # TODO: Iterate published jobs, fetch metrics from platform APIs
    # Create analytics_snapshots


@celery_app.task(name="refresh_tokens")
def refresh_tokens_task():
    """Refresh expiring OAuth tokens for platform accounts."""
    logger.info("Refreshing expiring tokens...")

    # TODO: Find platform_accounts with token_expires_at approaching
    # Refresh tokens using platform-specific flows
