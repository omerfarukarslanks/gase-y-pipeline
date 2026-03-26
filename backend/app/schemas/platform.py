import uuid
from datetime import datetime

from pydantic import BaseModel


class PlatformAccountResponse(BaseModel):
    id: uuid.UUID
    platform: str
    display_name: str | None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class PublishRequest(BaseModel):
    video_variant_id: uuid.UUID
    platform_account_ids: list[uuid.UUID]
    scheduled_at: datetime | None = None


class PublishJobResponse(BaseModel):
    id: uuid.UUID
    video_variant_id: uuid.UUID
    platform: str
    status: str
    scheduled_at: datetime | None
    published_at: datetime | None
    platform_url: str | None
    error_message: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
