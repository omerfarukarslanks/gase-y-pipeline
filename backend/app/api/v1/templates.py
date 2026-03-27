import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenException, NotFoundException
from app.db.session import get_db
from app.dependencies import get_current_user
from app.models.template import Template
from app.models.user import User
from app.schemas.template import TemplateCreate, TemplateResponse, TemplateUpdate

router = APIRouter(prefix="/templates", tags=["templates"])


@router.get("/", response_model=list[TemplateResponse])
async def list_templates(
    category: str | None = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List system templates and user's custom templates."""
    query = select(Template).where(
        or_(Template.is_system == True, Template.user_id == current_user.id)
    )
    if category:
        query = query.where(Template.category == category)
    query = query.order_by(Template.is_system.desc(), Template.created_at.desc())
    result = await db.execute(query)
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


@router.get("/categories")
async def list_categories(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all available template categories."""
    result = await db.execute(
        select(Template.category)
        .where(Template.category.isnot(None))
        .distinct()
    )
    categories = [row[0] for row in result.all()]
    return {"categories": categories}


@router.get("/{template_id}", response_model=TemplateResponse)
async def get_template(
    template_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Template).where(Template.id == template_id))
    template = result.scalar_one_or_none()
    if not template:
        raise NotFoundException("Template not found")
    # User can view system templates or their own
    if not template.is_system and template.user_id != current_user.id:
        raise ForbiddenException()
    return template


@router.put("/{template_id}", response_model=TemplateResponse)
async def update_template(
    template_id: uuid.UUID,
    data: TemplateUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a custom template (system templates cannot be modified)."""
    result = await db.execute(select(Template).where(Template.id == template_id))
    template = result.scalar_one_or_none()
    if not template:
        raise NotFoundException("Template not found")
    if template.is_system or template.user_id != current_user.id:
        raise ForbiddenException("Cannot modify this template")

    if data.name is not None:
        template.name = data.name
    if data.category is not None:
        template.category = data.category
    if data.description is not None:
        template.description = data.description
    if data.scene_structure is not None:
        template.scene_structure = data.scene_structure
    if data.default_settings is not None:
        template.default_settings = data.default_settings

    await db.flush()
    return template


@router.post("/{template_id}/duplicate", response_model=TemplateResponse)
async def duplicate_template(
    template_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Duplicate a template as a custom user template."""
    result = await db.execute(select(Template).where(Template.id == template_id))
    source = result.scalar_one_or_none()
    if not source:
        raise NotFoundException("Template not found")

    copy = Template(
        name=f"{source.name} (Copy)",
        category=source.category,
        description=source.description,
        scene_structure=source.scene_structure,
        default_settings=source.default_settings,
        is_system=False,
        user_id=current_user.id,
    )
    db.add(copy)
    await db.flush()
    return copy


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
