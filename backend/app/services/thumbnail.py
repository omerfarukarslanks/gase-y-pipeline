"""AI-powered thumbnail generation service."""

import logging
import os

from app.config import settings
from app.providers.image.factory import ImageProviderFactory

logger = logging.getLogger(__name__)


class ThumbnailService:
    def __init__(self, image_provider: str = "dalle"):
        self.provider = ImageProviderFactory.create(image_provider)

    async def generate_thumbnail(
        self,
        title: str,
        description: str,
        aspect_ratio: str = "16:9",
        style: str = "modern",
    ) -> bytes:
        """Generate a thumbnail image using AI.

        Args:
            title: Video title for context
            description: Video description/prompt
            aspect_ratio: Thumbnail aspect ratio
            style: Visual style (modern, minimal, bold, cinematic)

        Returns:
            Image bytes (PNG)
        """
        # Build a detailed thumbnail prompt
        prompt = (
            f"Create a professional YouTube video thumbnail. "
            f"Title: '{title}'. "
            f"Content: {description[:200]}. "
            f"Style: {style}, eye-catching, high contrast, clean composition. "
            f"No text in the image - the thumbnail should be purely visual."
        )

        # Map aspect ratio to dimensions
        dimensions = {
            "16:9": (1280, 720),
            "9:16": (720, 1280),
            "1:1": (1080, 1080),
        }
        width, height = dimensions.get(aspect_ratio, (1280, 720))

        image_bytes = await self.provider.generate_image(prompt, width, height)
        logger.info(f"Thumbnail generated ({len(image_bytes)} bytes)")
        return image_bytes

    async def generate_and_save(
        self,
        title: str,
        description: str,
        video_id: str,
        aspect_ratio: str = "16:9",
        style: str = "modern",
    ) -> str:
        """Generate and save thumbnail to disk.

        Returns:
            Path to saved thumbnail file
        """
        image_bytes = await self.generate_thumbnail(
            title, description, aspect_ratio, style
        )

        thumb_dir = os.path.join(settings.MEDIA_DIR, video_id, "thumbnails")
        os.makedirs(thumb_dir, exist_ok=True)

        thumb_path = os.path.join(thumb_dir, "thumbnail.png")
        with open(thumb_path, "wb") as f:
            f.write(image_bytes)

        logger.info(f"Thumbnail saved: {thumb_path}")
        return thumb_path
