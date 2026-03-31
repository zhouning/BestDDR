"""Industry template endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.financial import IndustryTemplate
from app.schemas.financial import (
    AssumptionItem,
    TemplateDetailResponse,
    TemplateResponse,
)

router = APIRouter(prefix="/api/templates", tags=["templates"])


@router.get("/", response_model=list[TemplateResponse])
async def list_templates(session: AsyncSession = Depends(get_db)):
    result = await session.execute(
        select(IndustryTemplate).order_by(IndustryTemplate.id)
    )
    return result.scalars().all()


@router.get("/{template_id}", response_model=TemplateDetailResponse)
async def get_template(template_id: int, session: AsyncSession = Depends(get_db)):
    result = await session.execute(
        select(IndustryTemplate)
        .where(IndustryTemplate.id == template_id)
        .options(selectinload(IndustryTemplate.default_assumptions))
    )
    tmpl = result.scalar_one_or_none()
    if not tmpl:
        raise HTTPException(status_code=404, detail="Template not found")

    return TemplateDetailResponse(
        id=tmpl.id,
        code=tmpl.code,
        name=tmpl.name,
        description=tmpl.description,
        default_assumptions=[
            AssumptionItem(
                param_key=a.param_key,
                display_name=a.display_name,
                category=a.category,
                param_value=a.param_value,
            )
            for a in tmpl.default_assumptions
        ],
    )
