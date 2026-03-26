"""Seed database with initial templates."""

import asyncio
import sys
sys.path.insert(0, "backend")

from app.config import settings
from app.db.session import async_session_factory
from app.models.template import Template


SYSTEM_TEMPLATES = [
    {
        "name": "Educational",
        "category": "education",
        "description": "Perfect for tutorials, explainers, and how-to videos",
        "scene_structure": {
            "scenes": [
                {"type": "intro", "duration_sec": 5, "style": "hook"},
                {"type": "content", "duration_sec": 20, "style": "explanation"},
                {"type": "summary", "duration_sec": 5, "style": "recap"},
            ]
        },
        "default_settings": {"aspect_ratio": "16:9", "tone": "informative"},
    },
    {
        "name": "Product Showcase",
        "category": "product",
        "description": "Highlight product features with dynamic visuals",
        "scene_structure": {
            "scenes": [
                {"type": "hook", "duration_sec": 3, "style": "attention_grab"},
                {"type": "features", "duration_sec": 15, "style": "showcase"},
                {"type": "cta", "duration_sec": 5, "style": "call_to_action"},
            ]
        },
        "default_settings": {"aspect_ratio": "9:16", "tone": "energetic"},
    },
    {
        "name": "News Update",
        "category": "news",
        "description": "Quick news format with key points",
        "scene_structure": {
            "scenes": [
                {"type": "headline", "duration_sec": 3, "style": "breaking"},
                {"type": "details", "duration_sec": 20, "style": "informative"},
                {"type": "closing", "duration_sec": 3, "style": "wrap_up"},
            ]
        },
        "default_settings": {"aspect_ratio": "16:9", "tone": "professional"},
    },
    {
        "name": "Motivational",
        "category": "motivation",
        "description": "Inspiring quotes and stories with emotional impact",
        "scene_structure": {
            "scenes": [
                {"type": "quote", "duration_sec": 5, "style": "dramatic"},
                {"type": "story", "duration_sec": 15, "style": "emotional"},
                {"type": "takeaway", "duration_sec": 5, "style": "uplifting"},
            ]
        },
        "default_settings": {"aspect_ratio": "9:16", "tone": "inspiring"},
    },
]


async def seed():
    async with async_session_factory() as session:
        for tmpl_data in SYSTEM_TEMPLATES:
            template = Template(
                name=tmpl_data["name"],
                category=tmpl_data["category"],
                description=tmpl_data["description"],
                scene_structure=tmpl_data["scene_structure"],
                default_settings=tmpl_data["default_settings"],
                is_system=True,
            )
            session.add(template)
        await session.commit()
        print(f"Seeded {len(SYSTEM_TEMPLATES)} templates.")


if __name__ == "__main__":
    asyncio.run(seed())
