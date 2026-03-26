"""FFmpeg helper utilities."""

import subprocess


def get_video_duration(file_path: str) -> float:
    """Get video duration in seconds."""
    result = subprocess.run(
        [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            file_path,
        ],
        capture_output=True,
        text=True,
    )
    return float(result.stdout.strip())


def get_video_info(file_path: str) -> dict:
    """Get video metadata (resolution, codec, duration)."""
    result = subprocess.run(
        [
            "ffprobe",
            "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=width,height,codec_name,duration",
            "-show_entries", "format=duration,size",
            "-of", "json",
            file_path,
        ],
        capture_output=True,
        text=True,
    )
    import json
    return json.loads(result.stdout)
