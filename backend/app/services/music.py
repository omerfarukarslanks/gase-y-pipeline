"""Background music library service.

Manages a collection of royalty-free background music tracks
organized by mood/category for video composition.
"""

import logging
import os

from app.config import settings

logger = logging.getLogger(__name__)

# Built-in music library metadata
# Tracks should be placed in MEDIA_DIR/music/
MUSIC_LIBRARY = [
    {
        "id": "upbeat-corporate",
        "name": "Upbeat Corporate",
        "category": "corporate",
        "mood": "upbeat",
        "duration_sec": 120,
        "filename": "upbeat_corporate.mp3",
    },
    {
        "id": "calm-ambient",
        "name": "Calm Ambient",
        "category": "ambient",
        "mood": "calm",
        "duration_sec": 180,
        "filename": "calm_ambient.mp3",
    },
    {
        "id": "inspiring-piano",
        "name": "Inspiring Piano",
        "category": "inspirational",
        "mood": "inspiring",
        "duration_sec": 150,
        "filename": "inspiring_piano.mp3",
    },
    {
        "id": "tech-electronic",
        "name": "Tech Electronic",
        "category": "technology",
        "mood": "energetic",
        "duration_sec": 120,
        "filename": "tech_electronic.mp3",
    },
    {
        "id": "news-intro",
        "name": "News Intro",
        "category": "news",
        "mood": "professional",
        "duration_sec": 60,
        "filename": "news_intro.mp3",
    },
    {
        "id": "soft-acoustic",
        "name": "Soft Acoustic",
        "category": "lifestyle",
        "mood": "warm",
        "duration_sec": 180,
        "filename": "soft_acoustic.mp3",
    },
    {
        "id": "cinematic-epic",
        "name": "Cinematic Epic",
        "category": "cinematic",
        "mood": "dramatic",
        "duration_sec": 120,
        "filename": "cinematic_epic.mp3",
    },
    {
        "id": "happy-ukulele",
        "name": "Happy Ukulele",
        "category": "casual",
        "mood": "happy",
        "duration_sec": 90,
        "filename": "happy_ukulele.mp3",
    },
]


class MusicLibrary:
    """Manages background music tracks for video composition."""

    def __init__(self):
        self.music_dir = os.path.join(settings.MEDIA_DIR, "music")
        os.makedirs(self.music_dir, exist_ok=True)

    def list_tracks(self, category: str | None = None, mood: str | None = None) -> list[dict]:
        """List available music tracks with optional filtering."""
        tracks = []
        for track in MUSIC_LIBRARY:
            if category and track["category"] != category:
                continue
            if mood and track["mood"] != mood:
                continue

            track_info = {**track}
            track_info["available"] = self._is_available(track["filename"])
            tracks.append(track_info)

        return tracks

    def get_track_path(self, track_id: str) -> str | None:
        """Get the file path for a music track by ID."""
        for track in MUSIC_LIBRARY:
            if track["id"] == track_id:
                path = os.path.join(self.music_dir, track["filename"])
                if os.path.exists(path):
                    return path
                logger.warning(f"Track file not found: {path}")
                return None
        return None

    def get_track_info(self, track_id: str) -> dict | None:
        """Get metadata for a music track."""
        for track in MUSIC_LIBRARY:
            if track["id"] == track_id:
                track_info = {**track}
                track_info["available"] = self._is_available(track["filename"])
                return track_info
        return None

    def get_categories(self) -> list[str]:
        """Get all available music categories."""
        return sorted(set(t["category"] for t in MUSIC_LIBRARY))

    def get_moods(self) -> list[str]:
        """Get all available mood tags."""
        return sorted(set(t["mood"] for t in MUSIC_LIBRARY))

    def _is_available(self, filename: str) -> bool:
        """Check if a music file exists on disk."""
        return os.path.exists(os.path.join(self.music_dir, filename))
