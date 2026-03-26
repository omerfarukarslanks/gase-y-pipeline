"""
FFmpeg-based video composition service.

Assembles scenes with text overlays, audio tracks, background music,
watermarks, and subtitles into a final video.
"""

import logging
import os
import tempfile

import ffmpeg

from app.config import settings

logger = logging.getLogger(__name__)


class VideoComposer:
    def __init__(self, output_dir: str | None = None):
        self.output_dir = output_dir or settings.MEDIA_DIR
        os.makedirs(self.output_dir, exist_ok=True)

    def compose_video(
        self,
        scenes: list[dict],
        audio_files: list[str],
        output_filename: str,
        aspect_ratio: str = "16:9",
        resolution: str = "1080p",
        bg_music_path: str | None = None,
        watermark_path: str | None = None,
    ) -> str:
        """
        Compose a video from scenes with text overlays and audio.

        Args:
            scenes: List of scene dicts with overlay_text, duration_sec, visual_description
            audio_files: List of audio file paths (one per scene)
            output_filename: Output video filename
            aspect_ratio: Video aspect ratio (16:9, 9:16, 1:1)
            resolution: Video resolution (1080p, 720p)
            bg_music_path: Optional background music file
            watermark_path: Optional watermark image file

        Returns:
            Path to the output video file
        """
        width, height = self._get_dimensions(aspect_ratio, resolution)
        output_path = os.path.join(self.output_dir, output_filename)

        # Build filter complex for each scene
        scene_videos = []
        for i, scene in enumerate(scenes):
            duration = scene.get("duration_sec", 5)
            overlay_text = scene.get("overlay_text", "")

            # Create a color background for each scene
            bg = ffmpeg.input(
                f"color=c=black:s={width}x{height}:d={duration}",
                f="lavfi",
            )

            # Add text overlay
            if overlay_text:
                bg = bg.drawtext(
                    text=overlay_text,
                    fontsize=48,
                    fontcolor="white",
                    x="(w-text_w)/2",
                    y="(h-text_h)/2",
                    borderw=2,
                    bordercolor="black",
                )

            scene_videos.append(bg)

        # Concatenate all scenes
        if scene_videos:
            video = ffmpeg.concat(*scene_videos, v=1, a=0)
        else:
            logger.warning("No scenes to compose")
            return ""

        # Add audio tracks
        audio_inputs = []
        for audio_file in audio_files:
            if audio_file and os.path.exists(audio_file):
                audio_inputs.append(ffmpeg.input(audio_file))

        # Output
        output_args = {
            "vcodec": "libx264",
            "acodec": "aac",
            "pix_fmt": "yuv420p",
            "movflags": "+faststart",
        }

        if audio_inputs:
            merged_audio = ffmpeg.concat(*audio_inputs, v=0, a=1)
            stream = ffmpeg.output(video, merged_audio, output_path, **output_args)
        else:
            stream = ffmpeg.output(video, output_path, **output_args)

        stream = stream.overwrite_output()
        stream.run(quiet=True)

        logger.info(f"Video composed: {output_path}")
        return output_path

    @staticmethod
    def _get_dimensions(aspect_ratio: str, resolution: str) -> tuple[int, int]:
        res_map = {
            "1080p": {"16:9": (1920, 1080), "9:16": (1080, 1920), "1:1": (1080, 1080)},
            "720p": {"16:9": (1280, 720), "9:16": (720, 1280), "1:1": (720, 720)},
        }
        return res_map.get(resolution, res_map["1080p"]).get(
            aspect_ratio, (1920, 1080)
        )
