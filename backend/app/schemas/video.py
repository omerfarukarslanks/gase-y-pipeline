import uuid
from datetime import datetime

from pydantic import BaseModel


class VideoGenerateRequest(BaseModel):
    project_id: uuid.UUID
    languages: list[str] = ["en"]
    aspect_ratio: str = "16:9"
    resolution: str = "1080p"
    ai_provider: str = "openai"
    tts_provider: str = "elevenlabs"


class VideoResponse(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    aspect_ratio: str
    resolution: str
    duration_sec: float | None
    thumbnail_url: str | None
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class VideoVariantResponse(BaseModel):
    id: uuid.UUID
    video_id: uuid.UUID
    language: str
    file_url: str | None
    title: str | None
    description: str | None
    hashtags: list[str] | None
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class AddVariantRequest(BaseModel):
    language: str
    tts_provider: str = "elevenlabs"
    tts_voice_id: str | None = None
