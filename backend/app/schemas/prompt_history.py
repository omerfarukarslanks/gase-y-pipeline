import uuid
from datetime import datetime

from pydantic import BaseModel


class PromptHistoryResponse(BaseModel):
    id: uuid.UUID
    prompt_text: str
    project_id: uuid.UUID | None
    is_favorite: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class PromptHistoryCreate(BaseModel):
    prompt_text: str
    project_id: uuid.UUID | None = None
