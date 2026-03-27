"""Subtitle generation service (SRT/VTT)."""

import logging
import os

from app.config import settings
from app.services.video_composer import generate_srt, generate_vtt

logger = logging.getLogger(__name__)


class SubtitleService:
    """Generates subtitle files from video scenes."""

    @staticmethod
    def generate_from_scenes(
        scenes: list[dict],
        video_id: str,
        language: str = "en",
        format: str = "srt",
    ) -> str:
        """Generate subtitle file from scene data.

        Args:
            scenes: List of scene dicts with narration and duration_sec
            video_id: Video ID for file organization
            language: Language code
            format: Subtitle format (srt or vtt)

        Returns:
            Path to saved subtitle file
        """
        if format == "vtt":
            content = generate_vtt(scenes)
            ext = "vtt"
        else:
            content = generate_srt(scenes)
            ext = "srt"

        sub_dir = os.path.join(settings.MEDIA_DIR, video_id, language, "subtitles")
        os.makedirs(sub_dir, exist_ok=True)

        sub_path = os.path.join(sub_dir, f"subtitles.{ext}")
        with open(sub_path, "w", encoding="utf-8") as f:
            f.write(content)

        logger.info(f"Subtitle file generated: {sub_path}")
        return sub_path

    @staticmethod
    def generate_both_formats(
        scenes: list[dict],
        video_id: str,
        language: str = "en",
    ) -> dict[str, str]:
        """Generate both SRT and VTT subtitle files.

        Returns:
            Dict with 'srt' and 'vtt' paths
        """
        srt_path = SubtitleService.generate_from_scenes(
            scenes, video_id, language, "srt"
        )
        vtt_path = SubtitleService.generate_from_scenes(
            scenes, video_id, language, "vtt"
        )
        return {"srt": srt_path, "vtt": vtt_path}
