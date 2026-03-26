import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequestException, NotFoundException
from app.db.session import get_db
from app.dependencies import get_current_user
from app.models.platform_account import PlatformAccount
from app.models.publish_job import PublishJob
from app.models.user import User
from app.models.video_variant import VideoVariant
from app.schemas.platform import PublishJobResponse, PublishRequest

router = APIRouter(prefix="/publish", tags=["publish"])


@router.post("/", response_model=list[PublishJobResponse])
async def publish_video(
    data: PublishRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Publish a video variant to one or more platforms."""
    # Verify variant exists
    result = await db.execute(
        select(VideoVariant).where(VideoVariant.id == data.video_variant_id)
    )
    variant = result.scalar_one_or_none()
    if not variant:
        raise NotFoundException("Video variant not found")
    if variant.status != "completed":
        raise BadRequestException("Video variant is not ready for publishing")

    jobs = []
    for account_id in data.platform_account_ids:
        # Verify account belongs to user
        result = await db.execute(
            select(PlatformAccount).where(
                PlatformAccount.id == account_id,
                PlatformAccount.user_id == current_user.id,
                PlatformAccount.is_active == True,
            )
        )
        account = result.scalar_one_or_none()
        if not account:
            raise NotFoundException(f"Platform account {account_id} not found or inactive")

        job = PublishJob(
            video_variant_id=data.video_variant_id,
            platform_account_id=account_id,
            platform=account.platform,
            scheduled_at=data.scheduled_at,
            status="scheduled" if data.scheduled_at else "pending",
        )
        db.add(job)
        await db.flush()
        jobs.append(job)

        # Dispatch immediately if not scheduled
        if not data.scheduled_at:
            from app.workers.publish_tasks import publish_video_task
            publish_video_task.delay(str(job.id))

    await db.flush()
    return jobs


@router.get("/jobs", response_model=list[PublishJobResponse])
async def list_publish_jobs(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List publish jobs for the current user."""
    offset = (page - 1) * per_page
    result = await db.execute(
        select(PublishJob)
        .join(PlatformAccount, PublishJob.platform_account_id == PlatformAccount.id)
        .where(PlatformAccount.user_id == current_user.id)
        .order_by(PublishJob.created_at.desc())
        .offset(offset)
        .limit(per_page)
    )
    return result.scalars().all()


@router.get("/jobs/{job_id}", response_model=PublishJobResponse)
async def get_publish_job(
    job_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(PublishJob)
        .join(PlatformAccount, PublishJob.platform_account_id == PlatformAccount.id)
        .where(PublishJob.id == job_id, PlatformAccount.user_id == current_user.id)
    )
    job = result.scalar_one_or_none()
    if not job:
        raise NotFoundException("Publish job not found")
    return job


@router.post("/jobs/{job_id}/retry", response_model=PublishJobResponse)
async def retry_publish_job(
    job_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retry a failed publish job."""
    result = await db.execute(
        select(PublishJob)
        .join(PlatformAccount, PublishJob.platform_account_id == PlatformAccount.id)
        .where(PublishJob.id == job_id, PlatformAccount.user_id == current_user.id)
    )
    job = result.scalar_one_or_none()
    if not job:
        raise NotFoundException("Publish job not found")
    if job.status != "failed":
        raise BadRequestException("Only failed jobs can be retried")

    job.status = "pending"
    job.error_message = None
    await db.flush()

    from app.workers.publish_tasks import publish_video_task
    publish_video_task.delay(str(job.id))

    return job


@router.delete("/jobs/{job_id}")
async def cancel_publish_job(
    job_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Cancel a scheduled publish job."""
    result = await db.execute(
        select(PublishJob)
        .join(PlatformAccount, PublishJob.platform_account_id == PlatformAccount.id)
        .where(PublishJob.id == job_id, PlatformAccount.user_id == current_user.id)
    )
    job = result.scalar_one_or_none()
    if not job:
        raise NotFoundException("Publish job not found")
    if job.status not in ("pending", "scheduled"):
        raise BadRequestException("Can only cancel pending or scheduled jobs")

    await db.delete(job)
    return {"message": "Publish job cancelled"}
