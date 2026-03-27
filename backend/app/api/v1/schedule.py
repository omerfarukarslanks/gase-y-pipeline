"""Content calendar & scheduling API."""

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequestException, NotFoundException
from app.db.session import get_db
from app.dependencies import get_current_user
from app.models.platform_account import PlatformAccount
from app.models.publish_job import PublishJob
from app.models.schedule import ABTest
from app.models.user import User
from app.models.video_variant import VideoVariant

router = APIRouter(prefix="/schedule", tags=["schedule"])


@router.get("/calendar")
async def get_calendar(
    start: datetime | None = Query(None, description="Start of date range"),
    end: datetime | None = Query(None, description="End of date range"),
    platform: str | None = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get scheduled and published events for the content calendar."""
    query = (
        select(
            PublishJob.id,
            PublishJob.platform,
            PublishJob.status,
            PublishJob.scheduled_at,
            PublishJob.published_at,
            PublishJob.platform_url,
            VideoVariant.title,
            VideoVariant.language,
        )
        .join(PlatformAccount, PublishJob.platform_account_id == PlatformAccount.id)
        .join(VideoVariant, PublishJob.video_variant_id == VideoVariant.id)
        .where(PlatformAccount.user_id == current_user.id)
    )

    if platform:
        query = query.where(PublishJob.platform == platform)

    # Filter by date range
    if start and end:
        query = query.where(
            # Include scheduled jobs in range or published jobs in range
            (
                (PublishJob.scheduled_at.isnot(None)) & (PublishJob.scheduled_at.between(start, end))
            )
            | (
                (PublishJob.published_at.isnot(None)) & (PublishJob.published_at.between(start, end))
            )
        )

    query = query.order_by(
        PublishJob.scheduled_at.asc().nullsfirst(),
        PublishJob.published_at.asc().nullsfirst(),
    )

    result = await db.execute(query)
    events = []
    for row in result.all():
        event_date = row.scheduled_at or row.published_at
        events.append({
            "id": str(row.id),
            "title": row.title or "Untitled",
            "language": row.language,
            "platform": row.platform,
            "status": row.status,
            "date": event_date.isoformat() if event_date else None,
            "scheduled_at": row.scheduled_at.isoformat() if row.scheduled_at else None,
            "published_at": row.published_at.isoformat() if row.published_at else None,
            "platform_url": row.platform_url,
        })

    return {"events": events}


@router.put("/jobs/{job_id}/reschedule")
async def reschedule_job(
    job_id: uuid.UUID,
    scheduled_at: datetime = Query(..., description="New scheduled time"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Reschedule a pending/scheduled publish job."""
    result = await db.execute(
        select(PublishJob)
        .join(PlatformAccount, PublishJob.platform_account_id == PlatformAccount.id)
        .where(PublishJob.id == job_id, PlatformAccount.user_id == current_user.id)
    )
    job = result.scalar_one_or_none()
    if not job:
        raise NotFoundException("Publish job not found")
    if job.status not in ("pending", "scheduled"):
        raise BadRequestException("Can only reschedule pending or scheduled jobs")

    if scheduled_at <= datetime.now(timezone.utc):
        raise BadRequestException("Scheduled time must be in the future")

    job.scheduled_at = scheduled_at
    job.status = "scheduled"
    await db.flush()

    return {
        "id": str(job.id),
        "status": job.status,
        "scheduled_at": job.scheduled_at.isoformat(),
    }


# ── A/B Testing ────────────────────────────────────────────────

@router.post("/ab-tests")
async def create_ab_test(
    project_id: uuid.UUID = Query(...),
    name: str = Query(...),
    variant_ids: list[uuid.UUID] = Query(...),
    metric: str = Query("views"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create an A/B test between video variants."""
    if len(variant_ids) < 2:
        raise BadRequestException("A/B test requires at least 2 variants")
    if metric not in ("views", "likes", "comments", "shares"):
        raise BadRequestException("Invalid metric")

    test = ABTest(
        project_id=project_id,
        name=name,
        variant_ids=variant_ids,
        metric=metric,
        status="running",
    )
    db.add(test)
    await db.flush()

    return {
        "id": str(test.id),
        "name": test.name,
        "variant_ids": [str(v) for v in test.variant_ids],
        "metric": test.metric,
        "status": test.status,
    }


@router.get("/ab-tests")
async def list_ab_tests(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List A/B tests for current user's projects."""
    from app.models.project import Project

    result = await db.execute(
        select(ABTest)
        .join(Project, ABTest.project_id == Project.id)
        .where(Project.user_id == current_user.id)
        .order_by(ABTest.created_at.desc())
    )
    tests = result.scalars().all()

    return [
        {
            "id": str(t.id),
            "project_id": str(t.project_id),
            "name": t.name,
            "variant_ids": [str(v) for v in t.variant_ids],
            "winner_id": str(t.winner_id) if t.winner_id else None,
            "metric": t.metric,
            "status": t.status,
            "created_at": t.created_at.isoformat(),
            "ended_at": t.ended_at.isoformat() if t.ended_at else None,
        }
        for t in tests
    ]


@router.post("/ab-tests/{test_id}/resolve")
async def resolve_ab_test(
    test_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Resolve an A/B test by comparing analytics and picking a winner."""
    from app.models.project import Project

    result = await db.execute(
        select(ABTest)
        .join(Project, ABTest.project_id == Project.id)
        .where(ABTest.id == test_id, Project.user_id == current_user.id)
    )
    test = result.scalar_one_or_none()
    if not test:
        raise NotFoundException("A/B test not found")
    if test.status != "running":
        raise BadRequestException("Test is not running")

    # Compare variants based on their publish job analytics
    from sqlalchemy import func
    from app.models.analytics import AnalyticsSnapshot

    best_id = None
    best_score = -1

    for variant_id in test.variant_ids:
        # Get total metric across all publish jobs for this variant
        metric_col = getattr(AnalyticsSnapshot, test.metric, AnalyticsSnapshot.views)
        agg = await db.execute(
            select(func.coalesce(func.sum(metric_col), 0))
            .join(PublishJob, AnalyticsSnapshot.publish_job_id == PublishJob.id)
            .where(PublishJob.video_variant_id == variant_id)
        )
        score = agg.scalar() or 0
        if score > best_score:
            best_score = score
            best_id = variant_id

    test.winner_id = best_id
    test.status = "completed"
    test.ended_at = datetime.now(timezone.utc)
    await db.flush()

    return {
        "id": str(test.id),
        "winner_id": str(test.winner_id) if test.winner_id else None,
        "status": test.status,
        "ended_at": test.ended_at.isoformat(),
    }
