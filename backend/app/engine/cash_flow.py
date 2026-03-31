"""
Cash Flow Statement Calculator (Indirect Method)

Derives the cash flow statement from the income statement, current and prior
balance sheets, and assumptions. Pure function — no DB access.
"""


def compute_cash_flow(
    prior: dict[str, float],
    current_is: dict[str, float],
    current_bs: dict[str, float],
    prior_bs: dict[str, float],
    assumptions: dict[str, float],
) -> dict[str, float]:
    """Compute cash flow statement using the indirect method.

    Args:
        prior: Prior year's full financial data (may include IS/BS/CF codes).
        current_is: Current year's income statement.
        current_bs: Current year's balance sheet (after balancing).
        prior_bs: Prior year's balance sheet.
        assumptions: Current year's assumption parameters.

    Returns:
        Dict mapping CF line_item_code -> computed value.
    """
    g = _safe_get

    # ═══════════════════════════════════════════════════════════
    # Operating Activities (indirect method adjustments)
    # ═══════════════════════════════════════════════════════════

    cf_o_001 = g(current_is, "IS_300")                          # Net profit
    cf_o_002 = g(current_is, "IS_014") + g(current_is, "IS_013")  # Impairment
    cf_o_003 = (
        g(prior_bs, "BS_A_204") * g(assumptions, "depreciation_rate") / 100
    )                                                            # Depreciation
    cf_o_004 = (
        g(prior_bs, "BS_A_207") * g(assumptions, "amortization_rate") / 100
    )                                                            # Amortization
    cf_o_005 = 0.0                                               # LT deferred exp
    cf_o_006 = -g(current_is, "IS_015")                          # Disposal loss (negate gain)
    cf_o_007 = -g(current_is, "IS_012")                          # FV change loss (negate gain)
    cf_o_008 = g(current_is, "IS_007")                           # Finance costs
    cf_o_009 = -g(current_is, "IS_011")                          # Investment loss (negate income)
    cf_o_010 = 0.0                                               # Deferred tax change

    # Working capital changes
    cf_o_011 = g(prior_bs, "BS_A_008") - g(current_bs, "BS_A_008")  # Inventory decrease

    cf_o_012 = (
        (g(prior_bs, "BS_A_004") - g(current_bs, "BS_A_004"))       # AR decrease
        + (g(prior_bs, "BS_A_006") - g(current_bs, "BS_A_006"))     # Prepayments decrease
        + (g(prior_bs, "BS_A_007") - g(current_bs, "BS_A_007"))     # Other receivables decrease
        + (g(prior_bs, "BS_A_009") - g(current_bs, "BS_A_009"))     # Contract assets decrease
    )

    cf_o_013 = (
        (g(current_bs, "BS_L_004") - g(prior_bs, "BS_L_004"))       # AP increase
        + (g(current_bs, "BS_L_006") - g(prior_bs, "BS_L_006"))     # Contract liabilities increase
        + (g(current_bs, "BS_L_007") - g(prior_bs, "BS_L_007"))     # Employee benefits increase
        + (g(current_bs, "BS_L_008") - g(prior_bs, "BS_L_008"))     # Taxes payable increase
        + (g(current_bs, "BS_L_009") - g(prior_bs, "BS_L_009"))     # Other payables increase
    )

    cf_o_014 = 0.0  # Others

    cf_o_100 = (
        cf_o_001 + cf_o_002 + cf_o_003 + cf_o_004 + cf_o_005
        + cf_o_006 + cf_o_007 + cf_o_008 + cf_o_009 + cf_o_010
        + cf_o_011 + cf_o_012 + cf_o_013 + cf_o_014
    )

    # ═══════════════════════════════════════════════════════════
    # Investing Activities
    # ═══════════════════════════════════════════════════════════

    cf_i_001 = 0.0  # Cash from investment recovery
    cf_i_002 = 0.0  # Cash from investment income
    cf_i_003 = 0.0  # Cash from disposal of PPE
    cf_i_004 = g(current_is, "IS_001") * g(assumptions, "capex_ratio") / 100  # Capex
    cf_i_005 = 0.0  # Cash paid for investments
    cf_i_006 = 0.0  # Other investing cash flows

    cf_i_100 = cf_i_001 + cf_i_002 + cf_i_003 - cf_i_004 - cf_i_005 + cf_i_006

    # ═══════════════════════════════════════════════════════════
    # Financing Activities
    # ═══════════════════════════════════════════════════════════

    net_debt_change_st = g(current_bs, "BS_L_001") - g(prior_bs, "BS_L_001")
    net_debt_change_lt = g(current_bs, "BS_L_201") - g(prior_bs, "BS_L_201")

    cf_f_001 = g(assumptions, "new_equity", 0.0)                 # Equity financing
    cf_f_002 = (
        max(0.0, net_debt_change_st) + max(0.0, net_debt_change_lt)
    )                                                            # New borrowings
    cf_f_003 = (
        abs(min(0.0, net_debt_change_st)) + abs(min(0.0, net_debt_change_lt))
    )                                                            # Debt repayments

    dividends = (
        max(0.0, g(current_is, "IS_300"))
        * g(assumptions, "dividend_payout_ratio") / 100
    )
    interest_paid = g(current_is, "IS_007")
    cf_f_004 = dividends + interest_paid                         # Dividends & interest

    cf_f_005 = 0.0                                               # Other financing

    cf_f_100 = cf_f_001 + cf_f_002 - cf_f_003 - cf_f_004 + cf_f_005

    # ═══════════════════════════════════════════════════════════
    # Summary
    # ═══════════════════════════════════════════════════════════

    cf_900 = cf_o_100 + cf_i_100 + cf_f_100                     # Net increase in cash
    cf_901 = g(prior_bs, "BS_A_001")                             # Opening cash
    cf_999 = cf_900 + cf_901                                     # Closing cash

    return {
        # Operating
        "CF_O_001": cf_o_001,
        "CF_O_002": cf_o_002,
        "CF_O_003": cf_o_003,
        "CF_O_004": cf_o_004,
        "CF_O_005": cf_o_005,
        "CF_O_006": cf_o_006,
        "CF_O_007": cf_o_007,
        "CF_O_008": cf_o_008,
        "CF_O_009": cf_o_009,
        "CF_O_010": cf_o_010,
        "CF_O_011": cf_o_011,
        "CF_O_012": cf_o_012,
        "CF_O_013": cf_o_013,
        "CF_O_014": cf_o_014,
        "CF_O_100": cf_o_100,
        # Investing
        "CF_I_001": cf_i_001,
        "CF_I_002": cf_i_002,
        "CF_I_003": cf_i_003,
        "CF_I_004": cf_i_004,
        "CF_I_005": cf_i_005,
        "CF_I_006": cf_i_006,
        "CF_I_100": cf_i_100,
        # Financing
        "CF_F_001": cf_f_001,
        "CF_F_002": cf_f_002,
        "CF_F_003": cf_f_003,
        "CF_F_004": cf_f_004,
        "CF_F_005": cf_f_005,
        "CF_F_100": cf_f_100,
        # Summary
        "CF_900": cf_900,
        "CF_901": cf_901,
        "CF_999": cf_999,
    }


def _safe_get(d: dict, key: str, default: float = 0.0) -> float:
    """Return float value from dict, defaulting to *default* if missing."""
    return float(d.get(key, default))
