"""Thumbnail generation and music library API endpoints."""

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.db.session import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.video import Video
from app.services.music import MusicLibrary

router = APIRouter(tags=["media"])


# ── Music Library ──────────────────────────────────────────────

@router.get("/music/tracks")
async def list_music_tracks(
    category: str | None = Query(None),
    mood: str | None = Query(None),
    current_user: User = Depends(get_current_user),
):
    """List available background music tracks."""
    library = MusicLibrary()
    return library.list_tracks(category=category, mood=mood)


@router.get("/music/categories")
async def list_music_categories(
    current_user: User = Depends(get_current_user),
):
    """List available music categories."""
    library = MusicLibrary()
    return {"categories": library.get_categories(), "moods": library.get_moods()}


@router.get("/music/tracks/{track_id}")
async def get_music_track(
    track_id: str,
    current_user: User = Depends(get_current_user),
):
    """Get info about a specific music track."""
    library = MusicLibrary()
    track = library.get_track_info(track_id)
    if not track:
        raise NotFoundException("Music track not found")
    return track


# ── Thumbnail Generation ───────────────────────────────────────

@router.post("/videos/{video_id}/thumbnail")
async def generate_thumbnail(
    video_id: uuid.UUID,
    image_provider: str = Query("dalle"),
    style: str = Query("modern"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate an AI thumbnail for a video."""
    result = await db.execute(select(Video).where(Video.id == video_id))
    video = result.scalar_one_or_none()
    if not video:
        raise NotFoundException("Video not found")

    # Trigger async thumbnail generation via Celery
    from app.workers.video_tasks import generate_thumbnail_task
    generate_thumbnail_task.delay(
        str(video_id), image_provider, style
    )

    return {"message": "Thumbnail generation started", "video_id": str(video_id)}


# ── Subtitles ──────────────────────────────────────────────────

@router.get("/videos/{video_id}/subtitles/{language}")
async def get_subtitles(
    video_id: uuid.UUID,
    language: str,
    format: str = Query("srt", regex="^(srt|vtt)$"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get subtitle file for a video variant."""
    import os
    from fastapi.responses import FileResponse
    from app.config import settings

    sub_path = os.path.join(
        settings.MEDIA_DIR, str(video_id), language, "subtitles", f"subtitles.{format}"
    )
    if not os.path.exists(sub_path):
        raise NotFoundException(f"Subtitles not found for {language}")

    return FileResponse(
        sub_path,
        media_type="text/plain",
        filename=f"subtitles_{language}.{format}",
    )


@router.post("/videos/{video_id}/subtitles/{language}")
async def generate_subtitles(
    video_id: uuid.UUID,
    language: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate subtitles for a video variant from its script."""
    from app.models.video_variant import VideoVariant

    result = await db.execute(select(Video).where(Video.id == video_id))
    video = result.scalar_one_or_none()
    if not video:
        raise NotFoundException("Video not found")

    if not video.script or "scenes" not in video.script:
        raise NotFoundException("Video script not available")

    # Check variant exists
    vresult = await db.execute(
        select(VideoVariant).where(
            VideoVariant.video_id == video_id,
            VideoVariant.language == language,
        )
    )
    variant = vresult.scalar_one_or_none()
    if not variant:
        raise NotFoundException(f"No variant for language: {language}")

    from app.services.subtitle import SubtitleService
    paths = SubtitleService.generate_both_formats(
        video.script["scenes"], str(video_id), language
    )

    variant.subtitle_url = paths["vtt"]
    await db.flush()

    return {"srt": paths["srt"], "vtt": paths["vtt"]}
