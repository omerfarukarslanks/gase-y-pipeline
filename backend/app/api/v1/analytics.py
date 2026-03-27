"""Analytics API - aggregated performance metrics."""

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies import get_current_user
from app.models.analytics import AnalyticsSnapshot
from app.models.platform_account import PlatformAccount
from app.models.project import Project
from app.models.publish_job import PublishJob
from app.models.user import User
from app.models.video import Video
from app.models.video_variant import VideoVariant

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/overview")
async def get_overview(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get aggregated analytics overview for current user."""
    # Total videos
    video_count = await db.execute(
        select(func.count(Video.id))
        .join(Project, Video.project_id == Project.id)
        .where(Project.user_id == current_user.id)
    )
    total_videos = video_count.scalar() or 0

    # Total published
    published_count = await db.execute(
        select(func.count(PublishJob.id))
        .join(PlatformAccount, PublishJob.platform_account_id == PlatformAccount.id)
        .where(
            PlatformAccount.user_id == current_user.id,
            PublishJob.status == "published",
        )
    )
    total_published = published_count.scalar() or 0

    # Aggregate analytics from latest snapshots per job
    # Use the latest snapshot for each publish job
    latest_snapshots = (
        select(
            AnalyticsSnapshot.publish_job_id,
            func.max(AnalyticsSnapshot.snapshot_at).label("latest"),
        )
        .join(PublishJob, AnalyticsSnapshot.publish_job_id == PublishJob.id)
        .join(PlatformAccount, PublishJob.platform_account_id == PlatformAccount.id)
        .where(PlatformAccount.user_id == current_user.id)
        .group_by(AnalyticsSnapshot.publish_job_id)
        .subquery()
    )

    agg_result = await db.execute(
        select(
            func.coalesce(func.sum(AnalyticsSnapshot.views), 0).label("total_views"),
            func.coalesce(func.sum(AnalyticsSnapshot.likes), 0).label("total_likes"),
            func.coalesce(func.sum(AnalyticsSnapshot.comments), 0).label("total_comments"),
            func.coalesce(func.sum(AnalyticsSnapshot.shares), 0).label("total_shares"),
        )
        .join(
            latest_snapshots,
            (AnalyticsSnapshot.publish_job_id == latest_snapshots.c.publish_job_id)
            & (AnalyticsSnapshot.snapshot_at == latest_snapshots.c.latest),
        )
    )
    row = agg_result.one()

    # Per-platform breakdown
    platform_result = await db.execute(
        select(
            PublishJob.platform,
            func.count(PublishJob.id).label("count"),
            func.coalesce(func.sum(AnalyticsSnapshot.views), 0).label("views"),
            func.coalesce(func.sum(AnalyticsSnapshot.likes), 0).label("likes"),
        )
        .outerjoin(AnalyticsSnapshot, AnalyticsSnapshot.publish_job_id == PublishJob.id)
        .join(PlatformAccount, PublishJob.platform_account_id == PlatformAccount.id)
        .where(
            PlatformAccount.user_id == current_user.id,
            PublishJob.status == "published",
        )
        .group_by(PublishJob.platform)
    )
    platforms = {}
    for prow in platform_result.all():
        platforms[prow.platform] = {
            "published": prow.count,
            "views": int(prow.views),
            "likes": int(prow.likes),
        }

    return {
        "total_videos": total_videos,
        "total_published": total_published,
        "total_views": int(row.total_views),
        "total_likes": int(row.total_likes),
        "total_comments": int(row.total_comments),
        "total_shares": int(row.total_shares),
        "platforms": platforms,
    }


@router.get("/jobs/{job_id}/snapshots")
async def get_job_analytics(
    job_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get analytics timeline for a specific publish job."""
    # Verify ownership
    result = await db.execute(
        select(PublishJob)
        .join(PlatformAccount, PublishJob.platform_account_id == PlatformAccount.id)
        .where(PublishJob.id == job_id, PlatformAccount.user_id == current_user.id)
    )
    job = result.scalar_one_or_none()
    if not job:
        from app.core.exceptions import NotFoundException
        raise NotFoundException("Publish job not found")

    snapshots = await db.execute(
        select(AnalyticsSnapshot)
        .where(AnalyticsSnapshot.publish_job_id == job_id)
        .order_by(AnalyticsSnapshot.snapshot_at.asc())
    )

    return [
        {
            "views": s.views,
            "likes": s.likes,
            "comments": s.comments,
            "shares": s.shares,
            "watch_time_sec": s.watch_time_sec,
            "snapshot_at": s.snapshot_at.isoformat(),
        }
        for s in snapshots.scalars().all()
    ]


@router.get("/top-performing")
async def get_top_performing(
    limit: int = Query(5, ge=1, le=20),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get top performing published videos by views."""
    result = await db.execute(
        select(
            PublishJob.id,
            PublishJob.platform,
            PublishJob.platform_url,
            PublishJob.published_at,
            VideoVariant.title,
            VideoVariant.language,
            func.coalesce(func.max(AnalyticsSnapshot.views), 0).label("views"),
            func.coalesce(func.max(AnalyticsSnapshot.likes), 0).label("likes"),
        )
        .join(PlatformAccount, PublishJob.platform_account_id == PlatformAccount.id)
        .join(VideoVariant, PublishJob.video_variant_id == VideoVariant.id)
        .outerjoin(AnalyticsSnapshot, AnalyticsSnapshot.publish_job_id == PublishJob.id)
        .where(
            PlatformAccount.user_id == current_user.id,
            PublishJob.status == "published",
        )
        .group_by(
            PublishJob.id, PublishJob.platform, PublishJob.platform_url,
            PublishJob.published_at, VideoVariant.title, VideoVariant.language,
        )
        .order_by(func.coalesce(func.max(AnalyticsSnapshot.views), 0).desc())
        .limit(limit)
    )

    return [
        {
            "job_id": str(r.id),
            "platform": r.platform,
            "platform_url": r.platform_url,
            "published_at": r.published_at.isoformat() if r.published_at else None,
            "title": r.title,
            "language": r.language,
            "views": int(r.views),
            "likes": int(r.likes),
        }
        for r in result.all()
    ]
