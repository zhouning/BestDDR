"""
Income Statement Calculator

Computes all IS line items for a single forecast year based on
prior-year data and current-year assumptions. Pure function — no DB access.
"""


def compute_income_statement(
    prior: dict[str, float],
    assumptions: dict[str, float],
    current_bs: dict[str, float] | None = None,
) -> dict[str, float]:
    """Compute income statement line items for one forecast year.

    Args:
        prior: Prior year's financial data keyed by line_item_code.
        assumptions: Current year's assumption parameters keyed by param_key.
        current_bs: Current year's balance sheet (used for interest calc on
                     updated debt). If None, falls back to prior year debt.

    Returns:
        Dict mapping IS line_item_code -> computed value.
    """
    g = _safe_get

    # ── Revenue & direct costs ───────────────────────────────
    revenue = g(prior, "IS_001") * (1 + g(assumptions, "revenue_growth_rate") / 100)
    cogs = revenue * (1 - g(assumptions, "gross_margin") / 100)
    tax_surcharges = revenue * g(assumptions, "tax_surcharge_ratio") / 100
    selling_exp = revenue * g(assumptions, "selling_expense_ratio") / 100
    admin_exp = revenue * g(assumptions, "admin_expense_ratio") / 100
    rnd_exp = revenue * g(assumptions, "rnd_expense_ratio") / 100

    # ── Finance costs (interest on debt) ─────────────────────
    # Use current BS debt if available (iterative refinement), else prior year.
    if current_bs is not None:
        st_debt = g(current_bs, "BS_L_001")
        lt_debt = g(current_bs, "BS_L_201")
    else:
        st_debt = g(prior, "BS_L_001")
        lt_debt = g(prior, "BS_L_201")

    finance_cost = (st_debt + lt_debt) * g(assumptions, "interest_rate") / 100

    # ── Items that default to zero unless overridden ─────────
    other_income = g(assumptions, "other_income", 0.0)
    investment_income = g(assumptions, "investment_income", 0.0)
    fv_change_gains = g(assumptions, "fv_change_gains", 0.0)
    credit_impairment = g(assumptions, "credit_impairment", 0.0)
    asset_impairment = g(assumptions, "asset_impairment", 0.0)
    asset_disposal_gains = g(assumptions, "asset_disposal_gains", 0.0)

    # ── Calculated subtotals ─────────────────────────────────
    operating_profit = (
        revenue
        - cogs
        - tax_surcharges
        - selling_exp
        - admin_exp
        - rnd_exp
        - finance_cost
        + other_income
        + investment_income
        + fv_change_gains
        - credit_impairment
        - asset_impairment
        + asset_disposal_gains
    )

    non_op_income = g(assumptions, "non_operating_income", 0.0)
    non_op_expense = g(assumptions, "non_operating_expense", 0.0)

    total_profit = operating_profit + non_op_income - non_op_expense
    income_tax = max(0.0, total_profit) * g(assumptions, "effective_tax_rate") / 100
    net_profit = total_profit - income_tax

    # ── Assemble result ──────────────────────────────────────
    return {
        "IS_001": revenue,
        "IS_002": cogs,
        "IS_003": tax_surcharges,
        "IS_004": selling_exp,
        "IS_005": admin_exp,
        "IS_006": rnd_exp,
        "IS_007": finance_cost,
        "IS_008": finance_cost,  # Interest expense = finance cost in simple model
        "IS_009": 0.0,           # Interest income
        "IS_010": other_income,
        "IS_011": investment_income,
        "IS_012": fv_change_gains,
        "IS_013": credit_impairment,
        "IS_014": asset_impairment,
        "IS_015": asset_disposal_gains,
        "IS_100": operating_profit,
        "IS_101": non_op_income,
        "IS_102": non_op_expense,
        "IS_200": total_profit,
        "IS_201": income_tax,
        "IS_300": net_profit,
    }


def _safe_get(d: dict, key: str, default: float = 0.0) -> float:
    """Return float value from dict, defaulting to *default* if missing."""
    return float(d.get(key, default))
