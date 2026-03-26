"""Multi-platform publish dispatcher."""

import logging

from app.providers.platforms.factory import PlatformPublisherFactory

logger = logging.getLogger(__name__)


class PublishService:
    @staticmethod
    async def publish_video(
        platform: str,
        credentials: dict,
        video_path: str,
        title: str,
        description: str,
        tags: list[str] | None = None,
        **kwargs,
    ) -> dict:
        """Publish a video to a specific platform."""
        publisher = PlatformPublisherFactory.create(platform, **credentials)
        logger.info(f"Publishing to {platform}...")

        result = await publisher.upload_video(
            video_path=video_path,
            title=title,
            description=description,
            tags=tags,
            **kwargs,
        )

        logger.info(f"Published to {platform}: {result.get('platform_url')}")
        return result
