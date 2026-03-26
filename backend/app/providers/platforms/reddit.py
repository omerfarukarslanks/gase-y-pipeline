import asyncpraw

from app.config import settings
from app.providers.base import BasePlatformPublisher


class RedditPublisher(BasePlatformPublisher):
    def __init__(self, refresh_token: str):
        self.reddit = asyncpraw.Reddit(
            client_id=settings.REDDIT_CLIENT_ID,
            client_secret=settings.REDDIT_CLIENT_SECRET,
            refresh_token=refresh_token,
            user_agent="gase-y-pipeline/0.1",
        )

    async def upload_video(
        self,
        video_path: str,
        title: str,
        description: str,
        tags: list[str] | None = None,
        **kwargs,
    ) -> dict:
        subreddit_name = kwargs.get("subreddit", "test")
        subreddit = await self.reddit.subreddit(subreddit_name)

        submission = await subreddit.submit_video(
            title=title,
            video_path=video_path,
        )

        return {
            "platform_post_id": submission.id,
            "platform_url": f"https://www.reddit.com{submission.permalink}",
        }

    async def get_oauth_url(self, state: str) -> str:
        return (
            f"https://www.reddit.com/api/v1/authorize"
            f"?client_id={settings.REDDIT_CLIENT_ID}"
            f"&response_type=code"
            f"&state={state}"
            f"&redirect_uri=http://localhost:8000/api/v1/platforms/reddit/callback"
            f"&duration=permanent"
            f"&scope=submit,read"
        )

    async def exchange_code(self, code: str) -> dict:
        import httpx

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://www.reddit.com/api/v1/access_token",
                auth=(settings.REDDIT_CLIENT_ID, settings.REDDIT_CLIENT_SECRET),
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": "http://localhost:8000/api/v1/platforms/reddit/callback",
                },
                headers={"User-Agent": "gase-y-pipeline/0.1"},
            )
            response.raise_for_status()
            return response.json()
