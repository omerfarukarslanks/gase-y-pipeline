import uuid
from datetime import datetime

from pydantic import BaseModel


class ProjectCreate(BaseModel):
    title: str
    prompt: str
    template_id: uuid.UUID | None = None
    settings: dict = {}


class ProjectUpdate(BaseModel):
    title: str | None = None
    settings: dict | None = None


class ProjectResponse(BaseModel):
    id: uuid.UUID
    title: str
    original_prompt: str
    analyzed_content: dict | None
    template_id: uuid.UUID | None
    status: str
    settings: dict
    created_at: datetime

    model_config = {"from_attributes": True}
