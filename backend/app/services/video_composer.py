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
        bg_music_volume: float = 0.15,
        watermark_path: str | None = None,
        watermark_position: str = "bottom_right",
        watermark_opacity: float = 0.7,
        watermark_scale: float = 0.1,
        subtitle_path: str | None = None,
        font_size: int = 48,
        font_color: str = "white",
        bg_color: str = "black",
    ) -> str:
        """
        Compose a video from scenes with text overlays, audio, watermark,
        background music, and optional subtitle burn-in.

        Args:
            scenes: List of scene dicts with overlay_text, duration_sec, visual_description, bg_color
            audio_files: List of audio file paths (one per scene)
            output_filename: Output video filename
            aspect_ratio: Video aspect ratio (16:9, 9:16, 1:1)
            resolution: Video resolution (1080p, 720p)
            bg_music_path: Optional background music file
            bg_music_volume: Background music volume (0.0-1.0)
            watermark_path: Optional watermark/logo image file (PNG with transparency)
            watermark_position: Position: top_left, top_right, bottom_left, bottom_right, center
            watermark_opacity: Watermark opacity (0.0-1.0)
            watermark_scale: Watermark size relative to video width (0.0-1.0)
            subtitle_path: Optional SRT/ASS subtitle file to burn in
            font_size: Text overlay font size
            font_color: Text overlay font color
            bg_color: Default background color

        Returns:
            Path to the output video file
        """
        width, height = self._get_dimensions(aspect_ratio, resolution)
        output_path = os.path.join(self.output_dir, output_filename)

        # Build video for each scene
        scene_videos = []
        for i, scene in enumerate(scenes):
            duration = scene.get("duration_sec", 5)
            overlay_text = scene.get("overlay_text", "")
            scene_bg = scene.get("bg_color", bg_color)
            bg_image = scene.get("bg_image")

            # Use background image if available, otherwise color
            if bg_image and os.path.exists(bg_image):
                bg = ffmpeg.input(bg_image, loop=1, t=duration)
                bg = bg.filter("scale", width, height)
                bg = bg.filter("setsar", "1")
            else:
                bg = ffmpeg.input(
                    f"color=c={scene_bg}:s={width}x{height}:d={duration}",
                    f="lavfi",
                )

            # Add text overlay
            if overlay_text:
                # Escape special characters for FFmpeg drawtext
                safe_text = overlay_text.replace("'", "\\'").replace(":", "\\:")
                bg = bg.drawtext(
                    text=safe_text,
                    fontsize=font_size,
                    fontcolor=font_color,
                    x="(w-text_w)/2",
                    y="(h-text_h)/2",
                    borderw=2,
                    bordercolor="black",
                )

            scene_videos.append(bg)

        # Concatenate all scenes
        if not scene_videos:
            logger.warning("No scenes to compose")
            return ""

        video = ffmpeg.concat(*scene_videos, v=1, a=0)

        # Apply watermark
        if watermark_path and os.path.exists(watermark_path):
            video = self._apply_watermark(
                video, watermark_path, width, height,
                watermark_position, watermark_opacity, watermark_scale,
            )

        # Burn in subtitles
        if subtitle_path and os.path.exists(subtitle_path):
            video = self._burn_subtitles(video, subtitle_path, font_size)

        # Build audio track
        audio_inputs = []
        for audio_file in audio_files:
            if audio_file and os.path.exists(audio_file):
                audio_inputs.append(ffmpeg.input(audio_file))

        # Output config
        output_args = {
            "vcodec": "libx264",
            "acodec": "aac",
            "pix_fmt": "yuv420p",
            "movflags": "+faststart",
        }

        if audio_inputs:
            merged_narration = ffmpeg.concat(*audio_inputs, v=0, a=1)

            # Mix background music with narration
            if bg_music_path and os.path.exists(bg_music_path):
                final_audio = self._mix_background_music(
                    merged_narration, bg_music_path, bg_music_volume
                )
            else:
                final_audio = merged_narration

            stream = ffmpeg.output(video, final_audio, output_path, **output_args)
        elif bg_music_path and os.path.exists(bg_music_path):
            # Only background music, no narration
            bg_audio = ffmpeg.input(bg_music_path)
            bg_audio = bg_audio.filter("volume", bg_music_volume)
            stream = ffmpeg.output(video, bg_audio, output_path, **output_args, shortest=None)
        else:
            stream = ffmpeg.output(video, output_path, **output_args)

        stream = stream.overwrite_output()
        stream.run(quiet=True)

        logger.info(f"Video composed: {output_path}")
        return output_path

    @staticmethod
    def _apply_watermark(
        video, watermark_path: str,
        video_width: int, video_height: int,
        position: str, opacity: float, scale: float,
    ):
        """Overlay a watermark/logo on the video."""
        wm_width = int(video_width * scale)

        watermark = ffmpeg.input(watermark_path)
        watermark = watermark.filter("scale", wm_width, -1)

        if opacity < 1.0:
            watermark = watermark.filter(
                "colorchannelmixer", aa=opacity
            )

        # Position mapping with padding
        pad = 20
        positions = {
            "top_left": (pad, pad),
            "top_right": (f"W-w-{pad}", pad),
            "bottom_left": (pad, f"H-h-{pad}"),
            "bottom_right": (f"W-w-{pad}", f"H-h-{pad}"),
            "center": ("(W-w)/2", "(H-h)/2"),
        }
        x, y = positions.get(position, positions["bottom_right"])

        return ffmpeg.overlay(video, watermark, x=x, y=y)

    @staticmethod
    def _mix_background_music(narration_stream, bg_music_path: str, volume: float):
        """Mix background music with narration audio."""
        bg_audio = ffmpeg.input(bg_music_path, stream_loop=-1)
        bg_audio = bg_audio.filter("volume", volume)
        return ffmpeg.filter([narration_stream, bg_audio], "amix", inputs=2, duration="first")

    @staticmethod
    def _burn_subtitles(video, subtitle_path: str, font_size: int):
        """Burn subtitles into the video."""
        # Escape path for FFmpeg subtitle filter
        safe_path = subtitle_path.replace("\\", "/").replace(":", "\\:")
        style = f"FontSize={font_size},PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,Outline=2"
        return video.filter("subtitles", safe_path, force_style=style)

    @staticmethod
    def _get_dimensions(aspect_ratio: str, resolution: str) -> tuple[int, int]:
        res_map = {
            "1080p": {"16:9": (1920, 1080), "9:16": (1080, 1920), "1:1": (1080, 1080)},
            "720p": {"16:9": (1280, 720), "9:16": (720, 1280), "1:1": (720, 720)},
        }
        return res_map.get(resolution, res_map["1080p"]).get(
            aspect_ratio, (1920, 1080)
        )


def generate_srt(scenes: list[dict], offset: float = 0.0) -> str:
    """Generate SRT subtitle content from scenes.

    Args:
        scenes: List of scene dicts with narration and duration_sec
        offset: Start time offset in seconds

    Returns:
        SRT formatted string
    """
    srt_lines = []
    current_time = offset

    for i, scene in enumerate(scenes):
        narration = scene.get("narration", "")
        if not narration:
            current_time += scene.get("duration_sec", 5)
            continue

        duration = scene.get("duration_sec", 5)
        start = _format_srt_time(current_time)
        end = _format_srt_time(current_time + duration)

        srt_lines.append(f"{i + 1}")
        srt_lines.append(f"{start} --> {end}")
        srt_lines.append(narration)
        srt_lines.append("")

        current_time += duration

    return "\n".join(srt_lines)


def generate_vtt(scenes: list[dict], offset: float = 0.0) -> str:
    """Generate WebVTT subtitle content from scenes.

    Args:
        scenes: List of scene dicts with narration and duration_sec
        offset: Start time offset in seconds

    Returns:
        WebVTT formatted string
    """
    vtt_lines = ["WEBVTT", ""]
    current_time = offset

    for i, scene in enumerate(scenes):
        narration = scene.get("narration", "")
        if not narration:
            current_time += scene.get("duration_sec", 5)
            continue

        duration = scene.get("duration_sec", 5)
        start = _format_vtt_time(current_time)
        end = _format_vtt_time(current_time + duration)

        vtt_lines.append(f"{start} --> {end}")
        vtt_lines.append(narration)
        vtt_lines.append("")

        current_time += duration

    return "\n".join(vtt_lines)


def _format_srt_time(seconds: float) -> str:
    """Format seconds to SRT time: HH:MM:SS,mmm"""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def _format_vtt_time(seconds: float) -> str:
    """Format seconds to VTT time: HH:MM:SS.mmm"""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d}.{ms:03d}"
