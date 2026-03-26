import uuid
from datetime import datetime

from pydantic import BaseModel


class TemplateCreate(BaseModel):
    name: str
    category: str | None = None
    description: str | None = None
    scene_structure: dict
    default_settings: dict = {}


class TemplateResponse(BaseModel):
    id: uuid.UUID
    name: str
    category: str | None
    description: str | None
    scene_structure: dict
    default_settings: dict
    is_system: bool
    created_at: datetime

    model_config = {"from_attributes": True}
