from app.providers.base import BasePlatformPublisher


class PlatformPublisherFactory:
    @classmethod
    def create(cls, platform: str, **credentials) -> BasePlatformPublisher:
        if platform == "youtube":
            from app.providers.platforms.youtube import YouTubePublisher
            return YouTubePublisher(
                access_token=credentials["access_token"],
                refresh_token=credentials.get("refresh_token"),
            )
        elif platform == "instagram":
            from app.providers.platforms.instagram import InstagramPublisher
            return InstagramPublisher(
                access_token=credentials["access_token"],
                ig_user_id=credentials["platform_user_id"],
            )
        elif platform == "twitter":
            from app.providers.platforms.twitter import TwitterPublisher
            return TwitterPublisher(
                access_token=credentials["access_token"],
                access_token_secret=credentials.get("access_token_secret", ""),
            )
        elif platform == "reddit":
            from app.providers.platforms.reddit import RedditPublisher
            return RedditPublisher(refresh_token=credentials["refresh_token"])
        elif platform == "tiktok":
            from app.providers.platforms.tiktok import TikTokPublisher
            return TikTokPublisher(access_token=credentials["access_token"])
        else:
            raise ValueError(f"Unknown platform: {platform}")

    @classmethod
    def available_platforms(cls) -> list[str]:
        return ["youtube", "instagram", "twitter", "reddit", "tiktok"]
