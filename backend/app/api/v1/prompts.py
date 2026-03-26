import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.db.session import get_db
from app.dependencies import get_current_user
from app.models.analytics import PromptHistory
from app.models.user import User
from app.schemas.prompt_history import PromptHistoryCreate, PromptHistoryResponse

router = APIRouter(prefix="/prompts", tags=["prompts"])


@router.get("/history", response_model=list[PromptHistoryResponse])
async def list_prompt_history(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List user's prompt history, most recent first."""
    offset = (page - 1) * per_page
    result = await db.execute(
        select(PromptHistory)
        .where(PromptHistory.user_id == current_user.id)
        .order_by(PromptHistory.created_at.desc())
        .offset(offset)
        .limit(per_page)
    )
    return result.scalars().all()


@router.get("/favorites", response_model=list[PromptHistoryResponse])
async def list_favorites(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List user's favorite prompts."""
    result = await db.execute(
        select(PromptHistory)
        .where(
            PromptHistory.user_id == current_user.id,
            PromptHistory.is_favorite == True,
        )
        .order_by(PromptHistory.created_at.desc())
    )
    return result.scalars().all()


@router.post("/", response_model=PromptHistoryResponse)
async def save_prompt(
    data: PromptHistoryCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Save a prompt to history."""
    entry = PromptHistory(
        user_id=current_user.id,
        prompt_text=data.prompt_text,
        project_id=data.project_id,
    )
    db.add(entry)
    await db.flush()
    return entry


@router.post("/{prompt_id}/favorite", response_model=PromptHistoryResponse)
async def toggle_favorite(
    prompt_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Toggle favorite status for a prompt."""
    result = await db.execute(
        select(PromptHistory).where(
            PromptHistory.id == prompt_id,
            PromptHistory.user_id == current_user.id,
        )
    )
    entry = result.scalar_one_or_none()
    if not entry:
        raise NotFoundException("Prompt not found")

    entry.is_favorite = not entry.is_favorite
    await db.flush()
    return entry


@router.delete("/{prompt_id}")
async def delete_prompt(
    prompt_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a prompt from history."""
    result = await db.execute(
        select(PromptHistory).where(
            PromptHistory.id == prompt_id,
            PromptHistory.user_id == current_user.id,
        )
    )
    entry = result.scalar_one_or_none()
    if not entry:
        raise NotFoundException("Prompt not found")

    await db.delete(entry)
    return {"message": "Prompt deleted"}
