import tweepy

from app.config import settings
from app.providers.base import BasePlatformPublisher


class TwitterPublisher(BasePlatformPublisher):
    def __init__(self, access_token: str, access_token_secret: str = ""):
        self.client = tweepy.Client(
            bearer_token=None,
            consumer_key=settings.TWITTER_CLIENT_ID,
            consumer_secret=settings.TWITTER_CLIENT_SECRET,
            access_token=access_token,
            access_token_secret=access_token_secret,
        )
        # v1.1 API for media upload
        auth = tweepy.OAuth1UserHandler(
            settings.TWITTER_CLIENT_ID,
            settings.TWITTER_CLIENT_SECRET,
            access_token,
            access_token_secret,
        )
        self.api_v1 = tweepy.API(auth)

    async def upload_video(
        self,
        video_path: str,
        title: str,
        description: str,
        tags: list[str] | None = None,
        **kwargs,
    ) -> dict:
        # Upload media via v1.1
        media = self.api_v1.media_upload(
            filename=video_path,
            media_category="tweet_video",
        )

        tweet_text = description[:280]
        if tags:
            hashtags = " ".join(f"#{tag}" for tag in tags[:5])
            tweet_text = f"{description[:250]}\n{hashtags}"[:280]

        response = self.client.create_tweet(text=tweet_text, media_ids=[media.media_id])

        tweet_id = response.data["id"]
        return {
            "platform_post_id": tweet_id,
            "platform_url": f"https://twitter.com/i/status/{tweet_id}",
        }

    async def get_oauth_url(self, state: str) -> str:
        oauth2_handler = tweepy.OAuth2UserHandler(
            client_id=settings.TWITTER_CLIENT_ID,
            redirect_uri=f"http://localhost:8000/api/v1/platforms/twitter/callback",
            scope=["tweet.read", "tweet.write", "users.read", "offline.access"],
        )
        return oauth2_handler.get_authorization_url()

    async def exchange_code(self, code: str) -> dict:
        oauth2_handler = tweepy.OAuth2UserHandler(
            client_id=settings.TWITTER_CLIENT_ID,
            redirect_uri=f"http://localhost:8000/api/v1/platforms/twitter/callback",
            scope=["tweet.read", "tweet.write", "users.read", "offline.access"],
        )
        token = oauth2_handler.fetch_token(code)
        return {
            "access_token": token["access_token"],
            "refresh_token": token.get("refresh_token"),
        }
