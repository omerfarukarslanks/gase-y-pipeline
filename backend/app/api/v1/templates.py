import uuid

from fastapi import APIRouter, Depends
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenException, NotFoundException
from app.db.session import get_db
from app.dependencies import get_current_user
from app.models.template import Template
from app.models.user import User
from app.schemas.template import TemplateCreate, TemplateResponse

router = APIRouter(prefix="/templates", tags=["templates"])


@router.get("/", response_model=list[TemplateResponse])
async def list_templates(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Template).where(
            or_(Template.is_system == True, Template.user_id == current_user.id)
        )
    )
    return result.scalars().all()


@router.post("/", response_model=TemplateResponse)
async def create_template(
    data: TemplateCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    template = Template(
        name=data.name,
        category=data.category,
        description=data.description,
        scene_structure=data.scene_structure,
        default_settings=data.default_settings,
        is_system=False,
        user_id=current_user.id,
    )
    db.add(template)
    await db.flush()
    return template


@router.get("/{template_id}", response_model=TemplateResponse)
async def get_template(
    template_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Template).where(Template.id == template_id))
    template = result.scalar_one_or_none()
    if not template:
        raise NotFoundException("Template not found")
    return template


@router.delete("/{template_id}")
async def delete_template(
    template_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Template).where(Template.id == template_id))
    template = result.scalar_one_or_none()
    if not template:
        raise NotFoundException("Template not found")
    if template.is_system or template.user_id != current_user.id:
        raise ForbiddenException("Cannot delete this template")

    await db.delete(template)
    return {"message": "Template deleted"}
