"""Company CRUD endpoints — protected by authentication."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.database import get_db
from app.models.financial import Company
from app.models.user import User
from app.schemas.financial import CompanyCreate, CompanyResponse, CompanyUpdate

router = APIRouter(prefix="/api/companies", tags=["companies"])


async def _get_own_company(
    company_id: int, user: User, session: AsyncSession
) -> Company:
    """Fetch a company, ensuring it belongs to the current user."""
    company = await session.get(Company, company_id)
    if not company or company.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


@router.post("/", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
async def create_company(
    body: CompanyCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    company = Company(
        name=body.name,
        industry_template_id=body.industry_template_id,
        owner_id=current_user.id,
    )
    session.add(company)
    await session.commit()
    await session.refresh(company)
    return company


@router.get("/", response_model=list[CompanyResponse])
async def list_companies(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    result = await session.execute(
        select(Company)
        .where(Company.owner_id == current_user.id)
        .order_by(Company.id)
    )
    return result.scalars().all()


@router.get("/{company_id}", response_model=CompanyResponse)
async def get_company(
    company_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    return await _get_own_company(company_id, current_user, session)


@router.put("/{company_id}", response_model=CompanyResponse)
async def update_company(
    company_id: int,
    body: CompanyUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    company = await _get_own_company(company_id, current_user, session)
    company.name = body.name
    await session.commit()
    await session.refresh(company)
    return company


@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_company(
    company_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    company = await _get_own_company(company_id, current_user, session)
    await session.delete(company)
    await session.commit()
