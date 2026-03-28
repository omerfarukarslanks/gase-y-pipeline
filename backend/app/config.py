from pathlib import Path
from pydantic_settings import BaseSettings
from typing import List

BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Gase-Y Pipeline"
    DEBUG: bool = False
    SECRET_KEY: str = "change-me-to-a-random-secret-key"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://gasey:gasey_secret@localhost:5432/gasey_pipeline"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # AI Providers
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""

    # TTS Providers
    ELEVENLABS_API_KEY: str = ""
    GOOGLE_TTS_CREDENTIALS_PATH: str = ""

    # Image Providers
    STABILITY_API_KEY: str = ""

    # Translation
    DEEPL_API_KEY: str = ""

    # YouTube
    YOUTUBE_CLIENT_ID: str = "774656483317-jc7pg4v8v9c6ifm8if2bc209o343385o.apps.googleusercontent.com"
    YOUTUBE_CLIENT_SECRET: str = "**R5WI"
    YOUTUBE_REDIRECT_URI: str = "http://localhost:8000/api/v1/platforms/youtube/callback"

    # Instagram
    INSTAGRAM_APP_ID: str = ""
    INSTAGRAM_APP_SECRET: str = ""

    # Twitter/X
    TWITTER_CLIENT_ID: str = ""
    TWITTER_CLIENT_SECRET: str = ""

    # Reddit
    REDDIT_CLIENT_ID: str = ""
    REDDIT_CLIENT_SECRET: str = ""

    # TikTok
    TIKTOK_CLIENT_KEY: str = ""
    TIKTOK_CLIENT_SECRET: str = ""

    # Storage
    S3_ENDPOINT: str = "http://localhost:9000"
    S3_ACCESS_KEY: str = "minioadmin"
    S3_SECRET_KEY: str = "minioadmin"
    S3_BUCKET: str = "gasey-media"
    S3_REGION: str = "us-east-1"

    # Media
    MEDIA_DIR: str = "./media"

    model_config = {
        "env_file": BASE_DIR / ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


settings = Settings()
