"""
Balance Sheet Calculator

Computes all BS line items for a single forecast year based on
prior-year balance sheet, current-year income statement, and assumptions.
Pure function — no DB access.
"""


def compute_balance_sheet(
    prior: dict[str, float],
    is_data: dict[str, float],
    assumptions: dict[str, float],
) -> dict[str, float]:
    """Compute balance sheet line items for one forecast year.

    Args:
        prior: Prior year's financial data keyed by line_item_code.
        is_data: Current year's income statement data.
        assumptions: Current year's assumption parameters.

    Returns:
        Dict mapping BS line_item_code -> computed value.
    """
    g = _safe_get

    revenue = g(is_data, "IS_001")
    cogs = g(is_data, "IS_002")
    net_profit = g(is_data, "IS_300")

    # ── Current Assets ───────────────────────────────────────
    # Cash is initially carried forward; will be overwritten by balancer / CF
    cash = g(prior, "BS_A_001")
    trading_fin_assets = g(prior, "BS_A_002")
    notes_receivable = g(prior, "BS_A_003")
    accounts_receivable = revenue / 365 * g(assumptions, "dso_days")
    receivables_financing = g(prior, "BS_A_005")
    prepayments = revenue * g(assumptions, "prepayment_ratio") / 100
    other_receivables = g(prior, "BS_A_007")
    inventory = cogs / 365 * g(assumptions, "dio_days")
    contract_assets = g(prior, "BS_A_009")
    other_current_assets = g(prior, "BS_A_010")

    total_current_assets = (
        cash
        + trading_fin_assets
        + notes_receivable
        + accounts_receivable
        + receivables_financing
        + prepayments
        + other_receivables
        + inventory
        + contract_assets
        + other_current_assets
    )

    # ── Non-current Assets ───────────────────────────────────
    lt_equity_inv = g(prior, "BS_A_201")
    other_nc_fin_assets = g(prior, "BS_A_202")
    investment_property = g(prior, "BS_A_203")

    capex = revenue * g(assumptions, "capex_ratio") / 100
    depreciation = g(prior, "BS_A_204") * g(assumptions, "depreciation_rate") / 100
    ppe = g(prior, "BS_A_204") + capex - depreciation

    construction_in_progress = g(prior, "BS_A_205")
    rou_assets = g(prior, "BS_A_206")

    amortization_rate = g(assumptions, "amortization_rate")
    intangibles = g(prior, "BS_A_207") * (1 - amortization_rate / 100)

    goodwill = g(prior, "BS_A_208")
    lt_deferred_exp = g(prior, "BS_A_209")
    deferred_tax_assets = g(prior, "BS_A_210")
    other_nc_assets = g(prior, "BS_A_211")

    total_noncurrent_assets = (
        lt_equity_inv
        + other_nc_fin_assets
        + investment_property
        + ppe
        + construction_in_progress
        + rou_assets
        + intangibles
        + goodwill
        + lt_deferred_exp
        + deferred_tax_assets
        + other_nc_assets
    )

    total_assets = total_current_assets + total_noncurrent_assets

    # ── Current Liabilities ──────────────────────────────────
    short_term_debt = g(assumptions, "short_term_debt")
    trading_fin_liab = g(prior, "BS_L_002")
    notes_payable = g(prior, "BS_L_003")
    accounts_payable = cogs / 365 * g(assumptions, "dpo_days")
    advances_from_cust = g(prior, "BS_L_005")
    contract_liabilities = revenue * g(assumptions, "contract_liability_ratio") / 100
    employee_benefits = g(prior, "BS_L_007")
    taxes_payable = g(prior, "BS_L_008")
    other_payables = g(prior, "BS_L_009")
    nc_liab_due_1yr = g(prior, "BS_L_010")
    other_current_liab = g(prior, "BS_L_011")

    total_current_liab = (
        short_term_debt
        + trading_fin_liab
        + notes_payable
        + accounts_payable
        + advances_from_cust
        + contract_liabilities
        + employee_benefits
        + taxes_payable
        + other_payables
        + nc_liab_due_1yr
        + other_current_liab
    )

    # ── Non-current Liabilities ──────────────────────────────
    long_term_debt = g(assumptions, "long_term_debt")
    bonds_payable = g(prior, "BS_L_202")
    lease_liab = g(prior, "BS_L_203")
    lt_payables = g(prior, "BS_L_204")
    provisions = g(prior, "BS_L_205")
    deferred_revenue = g(prior, "BS_L_206")
    deferred_tax_liab = g(prior, "BS_L_207")
    other_nc_liab = g(prior, "BS_L_208")

    total_noncurrent_liab = (
        long_term_debt
        + bonds_payable
        + lease_liab
        + lt_payables
        + provisions
        + deferred_revenue
        + deferred_tax_liab
        + other_nc_liab
    )

    total_liabilities = total_current_liab + total_noncurrent_liab

    # ── Equity ───────────────────────────────────────────────
    paid_in_capital = g(prior, "BS_E_001") + g(assumptions, "new_equity", 0.0)
    capital_reserve = g(prior, "BS_E_002")
    other_comp_income = g(prior, "BS_E_003")

    surplus_reserve_addition = (
        max(0.0, net_profit) * g(assumptions, "surplus_reserve_ratio") / 100
    )
    surplus_reserve = g(prior, "BS_E_004") + surplus_reserve_addition

    dividends = max(0.0, net_profit) * g(assumptions, "dividend_payout_ratio") / 100
    retained_earnings = (
        g(prior, "BS_E_005") + net_profit - dividends - surplus_reserve_addition
    )

    total_equity = (
        paid_in_capital
        + capital_reserve
        + other_comp_income
        + surplus_reserve
        + retained_earnings
    )

    total_liab_equity = total_liabilities + total_equity

    # ── Assemble result ──────────────────────────────────────
    return {
        # Current assets
        "BS_A_001": cash,
        "BS_A_002": trading_fin_assets,
        "BS_A_003": notes_receivable,
        "BS_A_004": accounts_receivable,
        "BS_A_005": receivables_financing,
        "BS_A_006": prepayments,
        "BS_A_007": other_receivables,
        "BS_A_008": inventory,
        "BS_A_009": contract_assets,
        "BS_A_010": other_current_assets,
        "BS_A_100": total_current_assets,
        # Non-current assets
        "BS_A_201": lt_equity_inv,
        "BS_A_202": other_nc_fin_assets,
        "BS_A_203": investment_property,
        "BS_A_204": ppe,
        "BS_A_205": construction_in_progress,
        "BS_A_206": rou_assets,
        "BS_A_207": intangibles,
        "BS_A_208": goodwill,
        "BS_A_209": lt_deferred_exp,
        "BS_A_210": deferred_tax_assets,
        "BS_A_211": other_nc_assets,
        "BS_A_300": total_noncurrent_assets,
        "BS_A_999": total_assets,
        # Current liabilities
        "BS_L_001": short_term_debt,
        "BS_L_002": trading_fin_liab,
        "BS_L_003": notes_payable,
        "BS_L_004": accounts_payable,
        "BS_L_005": advances_from_cust,
        "BS_L_006": contract_liabilities,
        "BS_L_007": employee_benefits,
        "BS_L_008": taxes_payable,
        "BS_L_009": other_payables,
        "BS_L_010": nc_liab_due_1yr,
        "BS_L_011": other_current_liab,
        "BS_L_100": total_current_liab,
        # Non-current liabilities
        "BS_L_201": long_term_debt,
        "BS_L_202": bonds_payable,
        "BS_L_203": lease_liab,
        "BS_L_204": lt_payables,
        "BS_L_205": provisions,
        "BS_L_206": deferred_revenue,
        "BS_L_207": deferred_tax_liab,
        "BS_L_208": other_nc_liab,
        "BS_L_300": total_noncurrent_liab,
        "BS_L_999": total_liabilities,
        # Equity
        "BS_E_001": paid_in_capital,
        "BS_E_002": capital_reserve,
        "BS_E_003": other_comp_income,
        "BS_E_004": surplus_reserve,
        "BS_E_005": retained_earnings,
        "BS_E_100": total_equity,
        # Grand total
        "BS_999": total_liab_equity,
    }


def recalculate_bs_subtotals(bs: dict[str, float]) -> dict[str, float]:
    """Recalculate all subtotal / total rows in a BS dict in place and return it.

    Used after the balancer adjusts individual items (cash or short-term debt).
    """
    g = _safe_get

    bs["BS_A_100"] = (
        g(bs, "BS_A_001")
        + g(bs, "BS_A_002")
        + g(bs, "BS_A_003")
        + g(bs, "BS_A_004")
        + g(bs, "BS_A_005")
        + g(bs, "BS_A_006")
        + g(bs, "BS_A_007")
        + g(bs, "BS_A_008")
        + g(bs, "BS_A_009")
        + g(bs, "BS_A_010")
    )
    bs["BS_A_300"] = (
        g(bs, "BS_A_201")
        + g(bs, "BS_A_202")
        + g(bs, "BS_A_203")
        + g(bs, "BS_A_204")
        + g(bs, "BS_A_205")
        + g(bs, "BS_A_206")
        + g(bs, "BS_A_207")
        + g(bs, "BS_A_208")
        + g(bs, "BS_A_209")
        + g(bs, "BS_A_210")
        + g(bs, "BS_A_211")
    )
    bs["BS_A_999"] = bs["BS_A_100"] + bs["BS_A_300"]

    bs["BS_L_100"] = (
        g(bs, "BS_L_001")
        + g(bs, "BS_L_002")
        + g(bs, "BS_L_003")
        + g(bs, "BS_L_004")
        + g(bs, "BS_L_005")
        + g(bs, "BS_L_006")
        + g(bs, "BS_L_007")
        + g(bs, "BS_L_008")
        + g(bs, "BS_L_009")
        + g(bs, "BS_L_010")
        + g(bs, "BS_L_011")
    )
    bs["BS_L_300"] = (
        g(bs, "BS_L_201")
        + g(bs, "BS_L_202")
        + g(bs, "BS_L_203")
        + g(bs, "BS_L_204")
        + g(bs, "BS_L_205")
        + g(bs, "BS_L_206")
        + g(bs, "BS_L_207")
        + g(bs, "BS_L_208")
    )
    bs["BS_L_999"] = bs["BS_L_100"] + bs["BS_L_300"]

    bs["BS_E_100"] = (
        g(bs, "BS_E_001")
        + g(bs, "BS_E_002")
        + g(bs, "BS_E_003")
        + g(bs, "BS_E_004")
        + g(bs, "BS_E_005")
    )

    bs["BS_999"] = bs["BS_L_999"] + bs["BS_E_100"]

    return bs


def _safe_get(d: dict, key: str, default: float = 0.0) -> float:
    """Return float value from dict, defaulting to *default* if missing."""
    return float(d.get(key, default))
