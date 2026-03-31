import enum

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class StatementType(str, enum.Enum):
    IS = "IS"  # Income Statement 利润表
    BS = "BS"  # Balance Sheet 资产负债表
    CF = "CF"  # Cash Flow 现金流量表


class LineItemType(str, enum.Enum):
    INPUT = "INPUT"
    CALCULATED = "CALCULATED"
    SUBTOTAL = "SUBTOTAL"


class PeriodType(str, enum.Enum):
    HISTORICAL = "HISTORICAL"
    PROJECTED = "PROJECTED"


# ── Industry Template ──────────────────────────────────────


class IndustryTemplate(Base):
    __tablename__ = "money_industry_templates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)

    companies: Mapped[list["Company"]] = relationship(back_populates="template")
    default_assumptions: Mapped[list["TemplateAssumption"]] = relationship(
        back_populates="template", cascade="all, delete-orphan"
    )
    line_items: Mapped[list["TemplateLineItem"]] = relationship(
        back_populates="template", cascade="all, delete-orphan"
    )


class TemplateAssumption(Base):
    __tablename__ = "money_template_assumptions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    template_id: Mapped[int] = mapped_column(ForeignKey("money_industry_templates.id"))
    param_key: Mapped[str] = mapped_column(String(100), nullable=False)
    param_value: Mapped[float] = mapped_column(Float, nullable=False)
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)  # IS/BS/CF

    template: Mapped["IndustryTemplate"] = relationship(
        back_populates="default_assumptions"
    )


class TemplateLineItem(Base):
    __tablename__ = "money_template_line_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    template_id: Mapped[int] = mapped_column(ForeignKey("money_industry_templates.id"))
    line_item_code: Mapped[str] = mapped_column(String(50), nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)

    template: Mapped["IndustryTemplate"] = relationship(back_populates="line_items")


# ── Line Item Definition (Global Dictionary) ───────────────


class LineItemDef(Base):
    __tablename__ = "money_line_item_defs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    statement_type: Mapped[StatementType] = mapped_column(
        Enum(StatementType), nullable=False
    )
    name_cn: Mapped[str] = mapped_column(String(100), nullable=False)
    name_en: Mapped[str] = mapped_column(String(200), nullable=False)
    parent_code: Mapped[str | None] = mapped_column(String(50))
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    item_type: Mapped[LineItemType] = mapped_column(
        Enum(LineItemType), default=LineItemType.INPUT
    )
    formula: Mapped[str | None] = mapped_column(Text)
    indent_level: Mapped[int] = mapped_column(Integer, default=0)
    is_bold: Mapped[bool] = mapped_column(Boolean, default=False)


# ── Company ────────────────────────────────────────────────


class Company(Base):
    __tablename__ = "money_companies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    industry_template_id: Mapped[int] = mapped_column(
        ForeignKey("money_industry_templates.id")
    )
    owner_id: Mapped[int | None] = mapped_column(
        ForeignKey("money_users.id"), nullable=True, index=True
    )
    created_at: Mapped[str] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[str] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    owner: Mapped["User | None"] = relationship(back_populates="companies")  # noqa: F821
    template: Mapped["IndustryTemplate"] = relationship(back_populates="companies")
    periods: Mapped[list["FinancialPeriod"]] = relationship(
        back_populates="company", cascade="all, delete-orphan"
    )
    scenarios: Mapped[list["ForecastScenario"]] = relationship(
        back_populates="company", cascade="all, delete-orphan"
    )


# ── Financial Period ───────────────────────────────────────


class FinancialPeriod(Base):
    __tablename__ = "money_financial_periods"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("money_companies.id"))
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    period_type: Mapped[PeriodType] = mapped_column(
        Enum(PeriodType), default=PeriodType.HISTORICAL
    )
    scenario_id: Mapped[int | None] = mapped_column(
        ForeignKey("money_forecast_scenarios.id")
    )

    company: Mapped["Company"] = relationship(back_populates="periods")
    scenario: Mapped["ForecastScenario | None"] = relationship(
        back_populates="periods"
    )
    data: Mapped[list["FinancialData"]] = relationship(
        back_populates="period", cascade="all, delete-orphan"
    )


# ── Financial Data (EAV row storage) ──────────────────────


class FinancialData(Base):
    __tablename__ = "money_financial_data"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    period_id: Mapped[int] = mapped_column(ForeignKey("money_financial_periods.id"))
    line_item_code: Mapped[str] = mapped_column(String(50), nullable=False)
    value: Mapped[float] = mapped_column(Float, default=0.0)
    is_override: Mapped[bool] = mapped_column(Boolean, default=False)

    period: Mapped["FinancialPeriod"] = relationship(back_populates="data")


# ── Forecast Scenario ─────────────────────────────────────


class ForecastScenario(Base):
    __tablename__ = "money_forecast_scenarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("money_companies.id"))
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[str] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    company: Mapped["Company"] = relationship(back_populates="scenarios")
    assumptions: Mapped[list["Assumption"]] = relationship(
        back_populates="scenario", cascade="all, delete-orphan"
    )
    periods: Mapped[list["FinancialPeriod"]] = relationship(
        back_populates="scenario", cascade="all, delete-orphan"
    )


# ── Assumption (per-year, per-scenario) ────────────────────


class Assumption(Base):
    __tablename__ = "money_assumptions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    scenario_id: Mapped[int] = mapped_column(ForeignKey("money_forecast_scenarios.id"))
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    param_key: Mapped[str] = mapped_column(String(100), nullable=False)
    param_value: Mapped[float] = mapped_column(Float, nullable=False)

    scenario: Mapped["ForecastScenario"] = relationship(back_populates="assumptions")
