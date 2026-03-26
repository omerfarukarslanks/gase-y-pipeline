import httpx

from app.config import settings
from app.providers.base import BasePlatformPublisher


class TikTokPublisher(BasePlatformPublisher):
    API_URL = "https://open.tiktokapis.com/v2"

    def __init__(self, access_token: str):
        self.access_token = access_token

    async def upload_video(
        self,
        video_path: str,
        title: str,
        description: str,
        tags: list[str] | None = None,
        **kwargs,
    ) -> dict:
        # TikTok Content Posting API
        async with httpx.AsyncClient() as client:
            # Step 1: Initialize upload
            init_response = await client.post(
                f"{self.API_URL}/post/publish/inbox/video/init/",
                headers={"Authorization": f"Bearer {self.access_token}"},
                json={
                    "post_info": {
                        "title": description[:150],
                        "privacy_level": "PUBLIC_TO_EVERYONE",
                    },
                    "source_info": {
                        "source": "FILE_UPLOAD",
                    },
                },
            )
            init_response.raise_for_status()
            upload_url = init_response.json()["data"]["upload_url"]

            # Step 2: Upload video file
            with open(video_path, "rb") as f:
                upload_response = await client.put(
                    upload_url,
                    content=f.read(),
                    headers={"Content-Type": "video/mp4"},
                )
                upload_response.raise_for_status()

            publish_id = init_response.json()["data"]["publish_id"]
            return {
                "platform_post_id": publish_id,
                "platform_url": "https://www.tiktok.com",
            }

    async def get_oauth_url(self, state: str) -> str:
        return (
            f"https://www.tiktok.com/v2/auth/authorize/"
            f"?client_key={settings.TIKTOK_CLIENT_KEY}"
            f"&scope=user.info.basic,video.publish"
            f"&response_type=code"
            f"&redirect_uri=http://localhost:8000/api/v1/platforms/tiktok/callback"
            f"&state={state}"
        )

    async def exchange_code(self, code: str) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.API_URL}/oauth/token/",
                json={
                    "client_key": settings.TIKTOK_CLIENT_KEY,
                    "client_secret": settings.TIKTOK_CLIENT_SECRET,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": "http://localhost:8000/api/v1/platforms/tiktok/callback",
                },
            )
            response.raise_for_status()
            return response.json()["data"]
