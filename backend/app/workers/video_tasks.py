"""Celery tasks for video generation pipeline."""

import asyncio
import logging
import os
import uuid

from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


def _run_async(coro):
    """Run an async coroutine from a sync Celery task."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


async def _generate_video_pipeline(video_id: str, ai_provider: str, tts_provider: str, task=None):
    """Full async video generation pipeline."""
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload

    from app.config import settings
    from app.db.session import async_session_factory
    from app.models.project import Project
    from app.models.video import Video
    from app.models.video_variant import VideoVariant
    from app.services.orchestrator import PipelineOrchestrator
    from app.services.video_composer import VideoComposer
    from app.utils.storage import get_storage

    storage = get_storage()
    composer = VideoComposer()

    async with async_session_factory() as db:
        # 1. Fetch video with variants and project
        result = await db.execute(
            select(Video).where(Video.id == uuid.UUID(video_id))
        )
        video = result.scalar_one_or_none()
        if not video:
            raise ValueError(f"Video {video_id} not found")

        result = await db.execute(
            select(Project).where(Project.id == video.project_id)
        )
        project = result.scalar_one_or_none()
        if not project:
            raise ValueError(f"Project for video {video_id} not found")

        result = await db.execute(
            select(VideoVariant).where(VideoVariant.video_id == video.id)
        )
        variants = result.scalars().all()

        # Get user_id for notifications
        user_id = str(project.user_id)

        # Update status
        video.status = "processing"
        project.status = "processing"
        await db.commit()

        # Send notification
        from app.utils.notifications import notify_video_progress
        notify_video_progress(user_id, video_id, "initializing")

        try:
            # 2. Analyze prompt and generate script
            if task:
                task.update_state(state="PROCESSING", meta={"step": "analyzing_prompt"})
            notify_video_progress(user_id, video_id, "analyzing_prompt")

            orchestrator = PipelineOrchestrator(ai_provider=ai_provider, tts_provider=tts_provider)
            script_result = await orchestrator.analyze_and_generate_script(project.original_prompt)

            video.script = script_result
            project.analyzed_content = script_result.get("analysis", {})
            await db.commit()

            scenes = script_result.get("scenes", [])

            # 3. For each language variant: translate → TTS → compose
            for variant in variants:
                if task:
                    task.update_state(
                        state="PROCESSING",
                        meta={"step": f"generating_{variant.language}"},
                    )

                # 3a. Translate script if not the base language
                if variant.language != "en":
                    translated_scenes = await orchestrator.translate_script(
                        scenes, variant.language
                    )
                    # Translate metadata
                    meta = await orchestrator.translate_metadata(
                        project.title, project.original_prompt, variant.language
                    )
                    variant.title = meta["title"]
                    variant.description = meta["description"]
                else:
                    translated_scenes = scenes
                    variant.title = project.title
                    variant.description = project.original_prompt

                variant.status = "generating_audio"
                await db.commit()

                # 3b. Generate TTS audio for each scene
                audio_clips = await orchestrator.generate_narration(
                    translated_scenes,
                    voice_id=variant.tts_voice_id,
                    language=variant.language,
                )

                # Save audio files to disk
                audio_dir = os.path.join(settings.MEDIA_DIR, str(video.id), variant.language, "audio")
                os.makedirs(audio_dir, exist_ok=True)
                audio_paths = []
                for i, clip in enumerate(audio_clips):
                    if clip:
                        path = os.path.join(audio_dir, f"scene_{i}.mp3")
                        with open(path, "wb") as f:
                            f.write(clip)
                        audio_paths.append(path)
                    else:
                        audio_paths.append("")

                # Save full narration audio
                if audio_clips and any(audio_clips):
                    full_audio = b"".join(c for c in audio_clips if c)
                    narration_path = os.path.join(audio_dir, "narration_full.mp3")
                    with open(narration_path, "wb") as f:
                        f.write(full_audio)
                    variant.narration_url = narration_path

                variant.status = "composing_video"
                await db.commit()

                # 3c. Compose video with FFmpeg
                output_filename = f"{video.id}_{variant.language}.mp4"
                video_path = composer.compose_video(
                    scenes=translated_scenes,
                    audio_files=audio_paths,
                    output_filename=output_filename,
                    aspect_ratio=video.aspect_ratio,
                    resolution=video.resolution,
                )

                if video_path and os.path.exists(video_path):
                    variant.file_url = video_path
                    variant.file_size_bytes = os.path.getsize(video_path)
                    variant.status = "completed"
                else:
                    variant.status = "failed"

                await db.commit()

            # 4. Calculate video duration from first completed variant
            for variant in variants:
                if variant.file_url and os.path.exists(variant.file_url):
                    try:
                        from app.utils.ffmpeg import get_video_duration
                        video.duration_sec = get_video_duration(variant.file_url)
                    except Exception:
                        pass
                    break

            # 5. Update final status
            all_completed = all(v.status == "completed" for v in variants)
            video.status = "completed" if all_completed else "partial"
            project.status = "ready"
            await db.commit()

            notify_video_progress(user_id, video_id, "completed", status="completed")
            logger.info(f"Video generation completed: {video_id}")
            return {"video_id": video_id, "status": video.status}

        except Exception as e:
            logger.error(f"Video generation failed for {video_id}: {e}")
            video.status = "failed"
            video.error_message = str(e)
            project.status = "failed"
            for variant in variants:
                if variant.status not in ("completed",):
                    variant.status = "failed"
            await db.commit()
            notify_video_progress(user_id, video_id, "failed", status="failed")
            raise


@celery_app.task(bind=True, name="generate_video", max_retries=2)
def generate_video_task(self, video_id: str, ai_provider: str, tts_provider: str):
    """
    Main video generation task.
    Orchestrates: analyze → script → translate → TTS → compose.
    """
    logger.info(f"Starting video generation for video_id={video_id}")
    self.update_state(state="PROCESSING", meta={"step": "initializing"})

    try:
        result = _run_async(
            _generate_video_pipeline(video_id, ai_provider, tts_provider, task=self)
        )
        return result
    except Exception as exc:
        logger.error(f"Video generation task failed: {exc}")
        raise self.retry(exc=exc, countdown=30)


async def _generate_single_variant(video_id: str, variant_id: str, language: str):
    """Generate a single language variant for an existing video."""
    from sqlalchemy import select

    from app.config import settings
    from app.db.session import async_session_factory
    from app.models.video import Video
    from app.models.video_variant import VideoVariant
    from app.services.orchestrator import PipelineOrchestrator
    from app.services.video_composer import VideoComposer

    async with async_session_factory() as db:
        result = await db.execute(select(Video).where(Video.id == uuid.UUID(video_id)))
        video = result.scalar_one_or_none()
        if not video or not video.script:
            raise ValueError(f"Video {video_id} not found or has no script")

        result = await db.execute(
            select(VideoVariant).where(VideoVariant.id == uuid.UUID(variant_id))
        )
        variant = result.scalar_one_or_none()
        if not variant:
            raise ValueError(f"Variant {variant_id} not found")

        scenes = video.script.get("scenes", [])
        ai_provider = "openai"  # Default, could be stored in project settings
        tts_provider = variant.tts_provider or "elevenlabs"

        orchestrator = PipelineOrchestrator(ai_provider=ai_provider, tts_provider=tts_provider)

        # Translate
        if language != "en":
            translated_scenes = await orchestrator.translate_script(scenes, language)
        else:
            translated_scenes = scenes

        variant.status = "generating_audio"
        await db.commit()

        # TTS
        audio_clips = await orchestrator.generate_narration(
            translated_scenes, voice_id=variant.tts_voice_id, language=language
        )

        audio_dir = os.path.join(settings.MEDIA_DIR, str(video.id), language, "audio")
        os.makedirs(audio_dir, exist_ok=True)
        audio_paths = []
        for i, clip in enumerate(audio_clips):
            if clip:
                path = os.path.join(audio_dir, f"scene_{i}.mp3")
                with open(path, "wb") as f:
                    f.write(clip)
                audio_paths.append(path)
            else:
                audio_paths.append("")

        variant.status = "composing_video"
        await db.commit()

        # Compose
        composer = VideoComposer()
        output_filename = f"{video.id}_{language}.mp4"
        video_path = composer.compose_video(
            scenes=translated_scenes,
            audio_files=audio_paths,
            output_filename=output_filename,
            aspect_ratio=video.aspect_ratio,
            resolution=video.resolution,
        )

        if video_path and os.path.exists(video_path):
            import os as _os
            variant.file_url = video_path
            variant.file_size_bytes = _os.path.getsize(video_path)
            variant.status = "completed"
        else:
            variant.status = "failed"

        await db.commit()
        return {"variant_id": variant_id, "status": variant.status}


@celery_app.task(bind=True, name="generate_variant", max_retries=2)
def generate_variant_task(self, video_id: str, variant_id: str, language: str):
    """Generate a single language variant for an existing video."""
    logger.info(f"Generating variant {variant_id} ({language}) for video {video_id}")
    try:
        result = _run_async(_generate_single_variant(video_id, variant_id, language))
        return result
    except Exception as exc:
        logger.error(f"Variant generation failed: {exc}")
        raise self.retry(exc=exc, countdown=30)
