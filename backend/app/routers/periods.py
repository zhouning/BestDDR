"""Historical period / financial data endpoints — protected by authentication."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.database import get_db
from app.models.financial import Company, FinancialData, FinancialPeriod, PeriodType
from app.models.user import User
from app.schemas.financial import (
    FinancialDataItem,
    PeriodCreate,
    PeriodDataResponse,
    PeriodDataUpdate,
    PeriodResponse,
)

router = APIRouter(
    prefix="/api/companies/{company_id}/periods", tags=["periods"]
)


async def _get_own_company(
    company_id: int, user: User, session: AsyncSession
) -> Company:
    company = await session.get(Company, company_id)
    if not company or company.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


async def _get_period(
    company_id: int, year: int, session: AsyncSession
) -> FinancialPeriod | None:
    result = await session.execute(
        select(FinancialPeriod).where(
            FinancialPeriod.company_id == company_id,
            FinancialPeriod.year == year,
            FinancialPeriod.period_type == PeriodType.HISTORICAL,
        )
    )
    return result.scalar_one_or_none()


@router.get("/", response_model=list[PeriodResponse])
async def list_periods(
    company_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    await _get_own_company(company_id, current_user, session)
    result = await session.execute(
        select(FinancialPeriod)
        .where(FinancialPeriod.company_id == company_id)
        .order_by(FinancialPeriod.year)
    )
    return result.scalars().all()


@router.post(
    "/", response_model=PeriodResponse, status_code=status.HTTP_201_CREATED
)
async def create_period(
    company_id: int,
    body: PeriodCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    await _get_own_company(company_id, current_user, session)

    existing = await _get_period(company_id, body.year, session)
    if existing:
        raise HTTPException(
            status_code=409,
            detail=f"Historical period for year {body.year} already exists",
        )

    period = FinancialPeriod(
        company_id=company_id,
        year=body.year,
        period_type=PeriodType.HISTORICAL,
    )
    session.add(period)
    await session.commit()
    await session.refresh(period)
    return period


@router.get("/{year}/data", response_model=PeriodDataResponse)
async def get_period_data(
    company_id: int,
    year: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    await _get_own_company(company_id, current_user, session)

    period = await _get_period(company_id, year, session)
    if not period:
        raise HTTPException(status_code=404, detail="Period not found")

    result = await session.execute(
        select(FinancialData).where(FinancialData.period_id == period.id)
    )
    rows = result.scalars().all()

    return PeriodDataResponse(
        year=period.year,
        period_type=period.period_type.value,
        data=[
            FinancialDataItem(
                line_item_code=r.line_item_code,
                value=r.value,
                is_override=r.is_override,
            )
            for r in rows
        ],
    )


@router.put("/{year}/data", response_model=PeriodDataResponse)
async def upsert_period_data(
    company_id: int,
    year: int,
    body: PeriodDataUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    await _get_own_company(company_id, current_user, session)

    period = await _get_period(company_id, year, session)
    if not period:
        raise HTTPException(status_code=404, detail="Period not found")

    # Load existing data keyed by line_item_code
    result = await session.execute(
        select(FinancialData).where(FinancialData.period_id == period.id)
    )
    existing = {r.line_item_code: r for r in result.scalars().all()}

    for item in body.items:
        if item.line_item_code in existing:
            row = existing[item.line_item_code]
            row.value = item.value
            row.is_override = item.is_override
        else:
            row = FinancialData(
                period_id=period.id,
                line_item_code=item.line_item_code,
                value=item.value,
                is_override=item.is_override,
            )
            session.add(row)
            existing[item.line_item_code] = row

    await session.commit()

    # Return refreshed data
    result = await session.execute(
        select(FinancialData).where(FinancialData.period_id == period.id)
    )
    rows = result.scalars().all()

    return PeriodDataResponse(
        year=period.year,
        period_type=period.period_type.value,
        data=[
            FinancialDataItem(
                line_item_code=r.line_item_code,
                value=r.value,
                is_override=r.is_override,
            )
            for r in rows
        ],
    )
