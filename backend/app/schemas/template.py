import uuid
from datetime import datetime

from pydantic import BaseModel


class TemplateCreate(BaseModel):
    name: str
    category: str | None = None
    description: str | None = None
    scene_structure: dict
    default_settings: dict = {}


class TemplateUpdate(BaseModel):
    name: str | None = None
    category: str | None = None
    description: str | None = None
    scene_structure: dict | None = None
    default_settings: dict | None = None


class TemplateResponse(BaseModel):
    id: uuid.UUID
    name: str
    category: str | None
    description: str | None
    scene_structure: dict
    default_settings: dict
    is_system: bool
    user_id: uuid.UUID | None
    created_at: datetime

    model_config = {"from_attributes": True}
