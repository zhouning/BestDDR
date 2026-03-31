"""Line item definition endpoints."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.financial import LineItemDef, StatementType
from app.schemas.financial import LineItemDefResponse

router = APIRouter(prefix="/api/line-items", tags=["line-items"])


@router.get("/", response_model=list[LineItemDefResponse])
async def list_line_items(
    statement_type: StatementType | None = Query(default=None),
    session: AsyncSession = Depends(get_db),
):
    stmt = select(LineItemDef).order_by(LineItemDef.sort_order)
    if statement_type is not None:
        stmt = stmt.where(LineItemDef.statement_type == statement_type)
    result = await session.execute(stmt)
    return result.scalars().all()
