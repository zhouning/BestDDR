"""Pydantic request / response schemas for the financial statement API."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


# ── Company ───────────────────────────────────────────────


class CompanyCreate(BaseModel):
    name: str
    industry_template_id: int


class CompanyUpdate(BaseModel):
    name: str


class CompanyResponse(BaseModel):
    id: int
    name: str
    industry_template_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ── Template ──────────────────────────────────────────────


class AssumptionItem(BaseModel):
    param_key: str
    display_name: str
    category: str
    param_value: float


class TemplateResponse(BaseModel):
    id: int
    code: str
    name: str
    description: str | None

    model_config = ConfigDict(from_attributes=True)


class TemplateDetailResponse(TemplateResponse):
    default_assumptions: list[AssumptionItem]


# ── Period / Data ─────────────────────────────────────────


class FinancialDataItem(BaseModel):
    line_item_code: str
    value: float
    is_override: bool = False


class PeriodDataResponse(BaseModel):
    year: int
    period_type: str
    data: list[FinancialDataItem]


class PeriodDataUpdate(BaseModel):
    items: list[FinancialDataItem]


class PeriodCreate(BaseModel):
    year: int


class PeriodResponse(BaseModel):
    id: int
    year: int
    period_type: str
    scenario_id: int | None

    model_config = ConfigDict(from_attributes=True)


# ── Scenario ──────────────────────────────────────────────


class ScenarioCreate(BaseModel):
    name: str


class ScenarioResponse(BaseModel):
    id: int
    name: str
    company_id: int

    model_config = ConfigDict(from_attributes=True)


# ── Assumptions ───────────────────────────────────────────


class AssumptionYearItem(BaseModel):
    year: int
    param_key: str
    param_value: float


class AssumptionUpdate(BaseModel):
    assumptions: list[AssumptionYearItem]


# ── Forecast ──────────────────────────────────────────────


class ForecastRequest(BaseModel):
    forecast_years: list[int]  # e.g. [2025, 2026, 2027]


# ── Statements ────────────────────────────────────────────


class LineItemRow(BaseModel):
    code: str
    name_cn: str
    name_en: str
    indent_level: int
    is_bold: bool
    values: dict[int, float]  # year -> value
    is_override: dict[int, bool]  # year -> whether overridden


class StatementResponse(BaseModel):
    statement_type: str  # IS, BS, CF
    rows: list[LineItemRow]
    years: list[int]
    period_types: dict[int, str]  # year -> HISTORICAL/PROJECTED


class StatementsResponse(BaseModel):
    income_statement: StatementResponse
    balance_sheet: StatementResponse
    cash_flow: StatementResponse


class OverrideRequest(BaseModel):
    year: int
    line_item_code: str
    value: float


# ── Line item definitions ────────────────────────────────


class LineItemDefResponse(BaseModel):
    code: str
    statement_type: str
    name_cn: str
    name_en: str
    parent_code: str | None
    sort_order: int
    item_type: str
    indent_level: int
    is_bold: bool

    model_config = ConfigDict(from_attributes=True)
