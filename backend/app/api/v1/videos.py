import uuid

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.db.session import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.video import Video
from app.models.video_variant import VideoVariant
from app.schemas.video import VideoGenerateRequest, VideoResponse, VideoVariantResponse

router = APIRouter(prefix="/videos", tags=["videos"])


@router.post("/", response_model=VideoResponse)
async def generate_video(
    data: VideoGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    video = Video(
        project_id=data.project_id,
        script={},
        aspect_ratio=data.aspect_ratio,
        resolution=data.resolution,
        status="pending",
    )
    db.add(video)
    await db.flush()

    # Create variants for each requested language
    for lang in data.languages:
        variant = VideoVariant(
            video_id=video.id,
            language=lang,
            tts_provider=data.tts_provider,
            status="pending",
        )
        db.add(variant)

    await db.flush()

    # Trigger Celery task for video generation
    from app.workers.video_tasks import generate_video_task
    generate_video_task.delay(str(video.id), data.ai_provider, data.tts_provider)

    video.status = "queued"
    await db.flush()

    return video


@router.get("/{video_id}", response_model=VideoResponse)
async def get_video(
    video_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Video).where(Video.id == video_id))
    video = result.scalar_one_or_none()
    if not video:
        raise NotFoundException("Video not found")
    return video


@router.get("/{video_id}/variants", response_model=list[VideoVariantResponse])
async def get_video_variants(
    video_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(VideoVariant).where(VideoVariant.video_id == video_id)
    )
    return result.scalars().all()
