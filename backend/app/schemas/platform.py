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


class PlatformPublishMetadata(BaseModel):
    """Per-platform metadata overrides for publishing."""
    title: str | None = None
    description: str | None = None
    tags: list[str] | None = None


class PublishRequest(BaseModel):
    video_variant_id: uuid.UUID
    platform_account_ids: list[uuid.UUID]
    scheduled_at: datetime | None = None
    platform_metadata: dict[str, PlatformPublishMetadata] | None = None


class PublishJobResponse(BaseModel):
    id: uuid.UUID
    video_variant_id: uuid.UUID
    platform_account_id: uuid.UUID
    platform: str
    status: str
    scheduled_at: datetime | None
    published_at: datetime | None
    platform_url: str | None
    platform_post_id: str | None
    error_message: str | None
    metadata: dict | None
    created_at: datetime

    model_config = {"from_attributes": True}


class MultiVariantPublishRequest(BaseModel):
    """Publish multiple variants to platforms at once (one variant per language)."""
    variant_ids: list[uuid.UUID]
    platform_account_ids: list[uuid.UUID]
    scheduled_at: datetime | None = None
