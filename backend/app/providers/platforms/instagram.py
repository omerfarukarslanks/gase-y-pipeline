import httpx

from app.config import settings
from app.providers.base import BasePlatformPublisher


class InstagramPublisher(BasePlatformPublisher):
    GRAPH_API_URL = "https://graph.facebook.com/v19.0"

    def __init__(self, access_token: str, ig_user_id: str):
        self.access_token = access_token
        self.ig_user_id = ig_user_id

    async def upload_video(
        self,
        video_path: str,
        title: str,
        description: str,
        tags: list[str] | None = None,
        **kwargs,
    ) -> dict:
        # Instagram Reels require a public URL for the video
        video_url = kwargs.get("video_url")
        if not video_url:
            raise ValueError("Instagram requires a publicly accessible video_url")

        caption = description
        if tags:
            caption += "\n\n" + " ".join(f"#{tag}" for tag in tags)

        async with httpx.AsyncClient() as client:
            # Step 1: Create container
            container_response = await client.post(
                f"{self.GRAPH_API_URL}/{self.ig_user_id}/media",
                params={
                    "media_type": "REELS",
                    "video_url": video_url,
                    "caption": caption,
                    "access_token": self.access_token,
                },
            )
            container_response.raise_for_status()
            container_id = container_response.json()["id"]

            # Step 2: Publish
            publish_response = await client.post(
                f"{self.GRAPH_API_URL}/{self.ig_user_id}/media_publish",
                params={
                    "creation_id": container_id,
                    "access_token": self.access_token,
                },
            )
            publish_response.raise_for_status()

            return {
                "platform_post_id": publish_response.json()["id"],
                "platform_url": f"https://www.instagram.com/reel/{publish_response.json()['id']}",
            }

    async def get_oauth_url(self, state: str) -> str:
        return (
            f"https://api.instagram.com/oauth/authorize"
            f"?client_id={settings.INSTAGRAM_APP_ID}"
            f"&redirect_uri={settings.YOUTUBE_REDIRECT_URI.replace('youtube', 'instagram')}"
            f"&scope=instagram_basic,instagram_content_publish"
            f"&response_type=code"
            f"&state={state}"
        )

    async def exchange_code(self, code: str) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.instagram.com/oauth/access_token",
                data={
                    "client_id": settings.INSTAGRAM_APP_ID,
                    "client_secret": settings.INSTAGRAM_APP_SECRET,
                    "grant_type": "authorization_code",
                    "redirect_uri": settings.YOUTUBE_REDIRECT_URI.replace("youtube", "instagram"),
                    "code": code,
                },
            )
            response.raise_for_status()
            return response.json()
