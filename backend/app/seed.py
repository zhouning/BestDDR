"""Seed the database with line item definitions and industry templates."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.engine.line_items import DEFAULT_ASSUMPTIONS, LINE_ITEMS
from app.models.financial import (
    IndustryTemplate,
    LineItemDef,
    TemplateAssumption,
    TemplateLineItem,
)


async def seed_line_items(session: AsyncSession) -> None:
    existing = (await session.execute(select(LineItemDef.code))).scalars().all()
    existing_codes = set(existing)

    for item in LINE_ITEMS:
        code = item[0]
        if code in existing_codes:
            continue
        session.add(
            LineItemDef(
                code=code,
                statement_type=item[1],
                name_cn=item[2],
                name_en=item[3],
                parent_code=item[4],
                sort_order=item[5],
                item_type=item[6],
                formula=item[7],
                indent_level=item[8],
                is_bold=item[9],
            )
        )
    await session.flush()


# ── Industry template definitions ─────────────────────────

INDUSTRY_TEMPLATES = [
    {
        "code": "general",
        "name": "General / 通用模板",
        "description": "Standard template suitable for most industries",
        "overrides": {},  # uses DEFAULT_ASSUMPTIONS as-is
    },
    {
        "code": "manufacturing",
        "name": "Manufacturing / 制造业",
        "description": "Heavy assets, long inventory cycles, high CapEx",
        "overrides": {
            "gross_margin": 30.0,
            "selling_expense_ratio": 5.0,
            "rnd_expense_ratio": 2.0,
            "dso_days": 75.0,
            "dio_days": 90.0,
            "dpo_days": 45.0,
            "capex_ratio": 10.0,
            "depreciation_rate": 8.0,
        },
    },
    {
        "code": "technology",
        "name": "Technology / 科技软件",
        "description": "High R&D, light assets, long receivable cycles",
        "overrides": {
            "gross_margin": 65.0,
            "selling_expense_ratio": 12.0,
            "admin_expense_ratio": 6.0,
            "rnd_expense_ratio": 15.0,
            "dso_days": 90.0,
            "dio_days": 15.0,
            "dpo_days": 30.0,
            "capex_ratio": 3.0,
            "prepayment_ratio": 1.0,
            "contract_liability_ratio": 8.0,
        },
    },
    {
        "code": "retail",
        "name": "Retail / 零售电商",
        "description": "Fast inventory turnover, low margins, high contract liabilities",
        "overrides": {
            "revenue_growth_rate": 15.0,
            "gross_margin": 25.0,
            "selling_expense_ratio": 10.0,
            "rnd_expense_ratio": 1.0,
            "dso_days": 15.0,
            "dio_days": 30.0,
            "dpo_days": 45.0,
            "capex_ratio": 4.0,
            "contract_liability_ratio": 10.0,
        },
    },
    {
        "code": "service",
        "name": "Service / 服务业",
        "description": "Light assets, high margins, people-intensive",
        "overrides": {
            "gross_margin": 55.0,
            "selling_expense_ratio": 10.0,
            "admin_expense_ratio": 8.0,
            "rnd_expense_ratio": 2.0,
            "dso_days": 45.0,
            "dio_days": 5.0,
            "dpo_days": 20.0,
            "capex_ratio": 2.0,
            "depreciation_rate": 15.0,
            "prepayment_ratio": 1.0,
        },
    },
]


async def _seed_template(session: AsyncSession, tmpl_def: dict) -> None:
    """Seed a single industry template if it doesn't exist."""
    result = await session.execute(
        select(IndustryTemplate).where(IndustryTemplate.code == tmpl_def["code"])
    )
    if result.scalar_one_or_none():
        return

    tmpl = IndustryTemplate(
        code=tmpl_def["code"],
        name=tmpl_def["name"],
        description=tmpl_def["description"],
    )
    session.add(tmpl)
    await session.flush()

    # Enable all line items
    for item in LINE_ITEMS:
        session.add(
            TemplateLineItem(
                template_id=tmpl.id, line_item_code=item[0], enabled=True
            )
        )

    # Add assumptions with industry-specific overrides
    overrides = tmpl_def.get("overrides", {})
    for key, display_name, category, default_value in DEFAULT_ASSUMPTIONS:
        value = overrides.get(key, default_value)
        session.add(
            TemplateAssumption(
                template_id=tmpl.id,
                param_key=key,
                param_value=value,
                display_name=display_name,
                category=category,
            )
        )
    await session.flush()


async def seed_all(session: AsyncSession) -> None:
    await seed_line_items(session)
    for tmpl_def in INDUSTRY_TEMPLATES:
        await _seed_template(session, tmpl_def)
    await session.commit()
