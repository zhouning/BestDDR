"""Scenario, assumptions, forecast, and statements endpoints — protected."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.auth import get_current_user
from app.database import get_db
from app.models.financial import (
    Assumption,
    Company,
    FinancialData,
    FinancialPeriod,
    ForecastScenario,
    LineItemDef,
    PeriodType,
    StatementType,
    TemplateAssumption,
)
from app.models.user import User
from app.schemas.financial import (
    AssumptionUpdate,
    AssumptionYearItem,
    ForecastRequest,
    LineItemRow,
    OverrideRequest,
    ScenarioCreate,
    ScenarioResponse,
    StatementResponse,
    StatementsResponse,
)

router = APIRouter(
    prefix="/api/companies/{company_id}/scenarios", tags=["scenarios"]
)


# ── helpers ───────────────────────────────────────────────


async def _get_own_company(
    company_id: int, user: User, session: AsyncSession
) -> Company:
    company = await session.get(Company, company_id)
    if not company or company.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


async def _get_scenario(
    company_id: int, scenario_id: int, session: AsyncSession
) -> ForecastScenario:
    result = await session.execute(
        select(ForecastScenario).where(
            ForecastScenario.id == scenario_id,
            ForecastScenario.company_id == company_id,
        )
    )
    scenario = result.scalar_one_or_none()
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    return scenario


# ── CRUD ──────────────────────────────────────────────────


@router.get("/", response_model=list[ScenarioResponse])
async def list_scenarios(
    company_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    await _get_own_company(company_id, current_user, session)
    result = await session.execute(
        select(ForecastScenario)
        .where(ForecastScenario.company_id == company_id)
        .order_by(ForecastScenario.id)
    )
    return result.scalars().all()


@router.post(
    "/", response_model=ScenarioResponse, status_code=status.HTTP_201_CREATED
)
async def create_scenario(
    company_id: int,
    body: ScenarioCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    company = await _get_own_company(company_id, current_user, session)

    # Check duplicate name
    existing = await session.execute(
        select(ForecastScenario).where(
            ForecastScenario.company_id == company_id,
            ForecastScenario.name == body.name,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Scenario '{body.name}' already exists",
        )

    scenario = ForecastScenario(company_id=company_id, name=body.name)
    session.add(scenario)
    await session.flush()

    # Copy template default assumptions into this scenario for a default year
    result = await session.execute(
        select(TemplateAssumption).where(
            TemplateAssumption.template_id == company.industry_template_id
        )
    )
    template_assumptions = result.scalars().all()

    # Find the latest historical year to use as starting point
    period_result = await session.execute(
        select(FinancialPeriod.year)
        .where(
            FinancialPeriod.company_id == company_id,
            FinancialPeriod.period_type == PeriodType.HISTORICAL,
        )
        .order_by(FinancialPeriod.year.desc())
        .limit(1)
    )
    latest_year = period_result.scalar_one_or_none()
    default_year = (latest_year + 1) if latest_year else 2025

    for ta in template_assumptions:
        session.add(
            Assumption(
                scenario_id=scenario.id,
                year=default_year,
                param_key=ta.param_key,
                param_value=ta.param_value,
            )
        )

    await session.commit()
    await session.refresh(scenario)
    return scenario


@router.delete("/{scenario_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_scenario(
    company_id: int,
    scenario_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    await _get_own_company(company_id, current_user, session)
    scenario = await _get_scenario(company_id, scenario_id, session)
    await session.delete(scenario)
    await session.commit()


# ── Assumptions ───────────────────────────────────────────


@router.get(
    "/{scenario_id}/assumptions", response_model=list[AssumptionYearItem]
)
async def get_assumptions(
    company_id: int,
    scenario_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    await _get_own_company(company_id, current_user, session)
    await _get_scenario(company_id, scenario_id, session)
    result = await session.execute(
        select(Assumption)
        .where(Assumption.scenario_id == scenario_id)
        .order_by(Assumption.year, Assumption.param_key)
    )
    rows = result.scalars().all()
    return [
        AssumptionYearItem(
            year=r.year, param_key=r.param_key, param_value=r.param_value
        )
        for r in rows
    ]


@router.put("/{scenario_id}/assumptions", response_model=list[AssumptionYearItem])
async def update_assumptions(
    company_id: int,
    scenario_id: int,
    body: AssumptionUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    await _get_own_company(company_id, current_user, session)
    await _get_scenario(company_id, scenario_id, session)

    # Load existing assumptions keyed by (year, param_key)
    result = await session.execute(
        select(Assumption).where(Assumption.scenario_id == scenario_id)
    )
    existing = {
        (r.year, r.param_key): r for r in result.scalars().all()
    }

    for item in body.assumptions:
        key = (item.year, item.param_key)
        if key in existing:
            existing[key].param_value = item.param_value
        else:
            row = Assumption(
                scenario_id=scenario_id,
                year=item.year,
                param_key=item.param_key,
                param_value=item.param_value,
            )
            session.add(row)

    await session.commit()

    # Return refreshed list
    result = await session.execute(
        select(Assumption)
        .where(Assumption.scenario_id == scenario_id)
        .order_by(Assumption.year, Assumption.param_key)
    )
    rows = result.scalars().all()
    return [
        AssumptionYearItem(
            year=r.year, param_key=r.param_key, param_value=r.param_value
        )
        for r in rows
    ]


# ── Forecast ──────────────────────────────────────────────


@router.post("/{scenario_id}/forecast", status_code=status.HTTP_200_OK)
async def run_forecast(
    company_id: int,
    scenario_id: int,
    body: ForecastRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    await _get_own_company(company_id, current_user, session)
    await _get_scenario(company_id, scenario_id, session)

    # Load the latest historical period data
    period_result = await session.execute(
        select(FinancialPeriod)
        .where(
            FinancialPeriod.company_id == company_id,
            FinancialPeriod.period_type == PeriodType.HISTORICAL,
        )
        .order_by(FinancialPeriod.year.desc())
        .limit(1)
        .options(selectinload(FinancialPeriod.data))
    )
    latest_period = period_result.scalar_one_or_none()
    if not latest_period:
        raise HTTPException(
            status_code=400, detail="No historical data found for forecasting"
        )

    historical_data = {
        d.line_item_code: d.value for d in latest_period.data
    }

    # Load assumptions for this scenario
    assumption_result = await session.execute(
        select(Assumption).where(Assumption.scenario_id == scenario_id)
    )
    assumptions_rows = assumption_result.scalars().all()
    assumptions_by_year: dict[int, dict[str, float]] = {}
    for a in assumptions_rows:
        assumptions_by_year.setdefault(a.year, {})[a.param_key] = a.param_value

    from app.engine.forecast import run_forecast as engine_run_forecast

    forecast_results = engine_run_forecast(
        historical_data=historical_data,
        assumptions_by_year=assumptions_by_year,
        forecast_years=body.forecast_years,
    )

    # Delete existing projected periods for this scenario + requested years
    existing_proj = await session.execute(
        select(FinancialPeriod).where(
            FinancialPeriod.company_id == company_id,
            FinancialPeriod.scenario_id == scenario_id,
            FinancialPeriod.period_type == PeriodType.PROJECTED,
            FinancialPeriod.year.in_(body.forecast_years),
        )
    )
    for old_period in existing_proj.scalars().all():
        await session.delete(old_period)
    await session.flush()

    # Save forecast results as PROJECTED periods
    for year in body.forecast_years:
        year_data = forecast_results.get(year, {})
        period = FinancialPeriod(
            company_id=company_id,
            year=year,
            period_type=PeriodType.PROJECTED,
            scenario_id=scenario_id,
        )
        session.add(period)
        await session.flush()

        for code, value in year_data.items():
            session.add(
                FinancialData(
                    period_id=period.id,
                    line_item_code=code,
                    value=value,
                    is_override=False,
                )
            )

    await session.commit()

    return {"status": "ok", "forecast_years": body.forecast_years}


# ── Statements ────────────────────────────────────────────


@router.get("/{scenario_id}/statements", response_model=StatementsResponse)
async def get_statements(
    company_id: int,
    scenario_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    await _get_own_company(company_id, current_user, session)
    await _get_scenario(company_id, scenario_id, session)

    # Load all periods: historical (no scenario) + projected for this scenario
    result = await session.execute(
        select(FinancialPeriod)
        .where(
            FinancialPeriod.company_id == company_id,
            (
                (FinancialPeriod.period_type == PeriodType.HISTORICAL)
                | (FinancialPeriod.scenario_id == scenario_id)
            ),
        )
        .options(selectinload(FinancialPeriod.data))
        .order_by(FinancialPeriod.year)
    )
    periods = result.scalars().all()

    if not periods:
        raise HTTPException(status_code=404, detail="No period data found")

    years = sorted({p.year for p in periods})
    period_types: dict[int, str] = {}
    data_map: dict[str, dict[int, tuple[float, bool]]] = {}

    for p in periods:
        period_types[p.year] = p.period_type.value
        for d in p.data:
            data_map.setdefault(d.line_item_code, {})[p.year] = (
                d.value,
                d.is_override,
            )

    # Load line item definitions
    lid_result = await session.execute(
        select(LineItemDef).order_by(LineItemDef.sort_order)
    )
    line_items = lid_result.scalars().all()

    def build_statement(st: StatementType) -> StatementResponse:
        rows: list[LineItemRow] = []
        for li in line_items:
            if li.statement_type != st:
                continue
            code_data = data_map.get(li.code, {})
            values: dict[int, float] = {}
            is_override: dict[int, bool] = {}
            for y in years:
                if y in code_data:
                    values[y] = code_data[y][0]
                    is_override[y] = code_data[y][1]
                else:
                    values[y] = 0.0
                    is_override[y] = False
            rows.append(
                LineItemRow(
                    code=li.code,
                    name_cn=li.name_cn,
                    name_en=li.name_en,
                    indent_level=li.indent_level,
                    is_bold=li.is_bold,
                    values=values,
                    is_override=is_override,
                )
            )
        return StatementResponse(
            statement_type=st.value,
            rows=rows,
            years=years,
            period_types=period_types,
        )

    return StatementsResponse(
        income_statement=build_statement(StatementType.IS),
        balance_sheet=build_statement(StatementType.BS),
        cash_flow=build_statement(StatementType.CF),
    )


# ── Overrides ─────────────────────────────────────────────


@router.put("/{scenario_id}/overrides", status_code=status.HTTP_200_OK)
async def override_value(
    company_id: int,
    scenario_id: int,
    body: OverrideRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    await _get_own_company(company_id, current_user, session)
    await _get_scenario(company_id, scenario_id, session)

    result = await session.execute(
        select(FinancialPeriod).where(
            FinancialPeriod.company_id == company_id,
            FinancialPeriod.scenario_id == scenario_id,
            FinancialPeriod.year == body.year,
            FinancialPeriod.period_type == PeriodType.PROJECTED,
        )
    )
    period = result.scalar_one_or_none()
    if not period:
        raise HTTPException(
            status_code=404,
            detail=f"No projected period found for year {body.year}",
        )

    data_result = await session.execute(
        select(FinancialData).where(
            FinancialData.period_id == period.id,
            FinancialData.line_item_code == body.line_item_code,
        )
    )
    row = data_result.scalar_one_or_none()

    if row:
        row.value = body.value
        row.is_override = True
    else:
        session.add(
            FinancialData(
                period_id=period.id,
                line_item_code=body.line_item_code,
                value=body.value,
                is_override=True,
            )
        )

    await session.commit()
    return {"status": "ok"}


# ── Validation ────────────────────────────────────────────


@router.get("/{scenario_id}/validation")
async def validate_balance_sheet(
    company_id: int,
    scenario_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    await _get_own_company(company_id, current_user, session)
    await _get_scenario(company_id, scenario_id, session)

    result = await session.execute(
        select(FinancialPeriod)
        .where(
            FinancialPeriod.company_id == company_id,
            (
                (FinancialPeriod.period_type == PeriodType.HISTORICAL)
                | (FinancialPeriod.scenario_id == scenario_id)
            ),
        )
        .options(selectinload(FinancialPeriod.data))
        .order_by(FinancialPeriod.year)
    )
    periods = result.scalars().all()

    checks: list[dict] = []
    for p in periods:
        data_by_code = {d.line_item_code: d.value for d in p.data}
        total_assets = data_by_code.get("BS_A_999", 0.0)
        total_liab_equity = data_by_code.get("BS_999", 0.0)
        balanced = abs(total_assets - total_liab_equity) < 0.01
        checks.append(
            {
                "year": p.year,
                "period_type": p.period_type.value,
                "total_assets": total_assets,
                "total_liabilities_equity": total_liab_equity,
                "balanced": balanced,
                "difference": round(total_assets - total_liab_equity, 2),
            }
        )

    all_balanced = all(c["balanced"] for c in checks)
    return {"balanced": all_balanced, "details": checks}
