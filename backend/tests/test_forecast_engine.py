"""Tests for the three-statement forecast engine."""

from app.engine.balance_sheet import compute_balance_sheet
from app.engine.balancer import auto_balance
from app.engine.cash_flow import compute_cash_flow
from app.engine.forecast import ForecastEngine, run_forecast
from app.engine.income_statement import compute_income_statement


# ── Sample data ──────────────────────────────────────────────

HISTORICAL = {
    # Income Statement
    "IS_001": 100_000,  # Revenue
    "IS_002": 60_000,   # COGS
    "IS_300": 15_000,   # Net profit
    # Balance Sheet — Assets
    "BS_A_001": 20_000,  # Cash
    "BS_A_004": 16_438,  # AR (DSO=60 → 100000/365*60)
    "BS_A_006": 2_000,   # Prepayments
    "BS_A_008": 7_397,   # Inventory (DIO=45 → 60000/365*45)
    "BS_A_204": 50_000,  # PPE
    "BS_A_207": 10_000,  # Intangibles
    # Balance Sheet — Liabilities
    "BS_L_001": 5_000,   # Short-term debt
    "BS_L_004": 4_932,   # AP (DPO=30 → 60000/365*30)
    "BS_L_006": 3_000,   # Contract liabilities
    "BS_L_201": 20_000,  # Long-term debt
    # Balance Sheet — Equity
    "BS_E_001": 30_000,  # Paid-in capital
    "BS_E_002": 5_000,   # Capital reserve
    "BS_E_004": 3_000,   # Surplus reserve
    "BS_E_005": 35_903,  # Retained earnings
}

ASSUMPTIONS = {
    "revenue_growth_rate": 10.0,
    "gross_margin": 40.0,
    "selling_expense_ratio": 8.0,
    "admin_expense_ratio": 5.0,
    "rnd_expense_ratio": 3.0,
    "tax_surcharge_ratio": 1.5,
    "effective_tax_rate": 25.0,
    "dso_days": 60.0,
    "dio_days": 45.0,
    "dpo_days": 30.0,
    "capex_ratio": 5.0,
    "depreciation_rate": 10.0,
    "amortization_rate": 10.0,
    "prepayment_ratio": 2.0,
    "contract_liability_ratio": 3.0,
    "dividend_payout_ratio": 30.0,
    "surplus_reserve_ratio": 10.0,
    "interest_rate": 4.5,
    "short_term_debt": 5_000.0,
    "long_term_debt": 20_000.0,
    "new_equity": 0.0,
}


# ── Income Statement tests ───────────────────────────────────


def test_is_revenue_growth():
    result = compute_income_statement(HISTORICAL, ASSUMPTIONS)
    expected_revenue = 100_000 * 1.10
    assert abs(result["IS_001"] - expected_revenue) < 0.01


def test_is_cogs_from_gross_margin():
    result = compute_income_statement(HISTORICAL, ASSUMPTIONS)
    revenue = result["IS_001"]
    expected_cogs = revenue * (1 - 0.40)
    assert abs(result["IS_002"] - expected_cogs) < 0.01


def test_is_expense_ratios():
    result = compute_income_statement(HISTORICAL, ASSUMPTIONS)
    revenue = result["IS_001"]
    assert abs(result["IS_004"] - revenue * 0.08) < 0.01  # Selling
    assert abs(result["IS_005"] - revenue * 0.05) < 0.01  # Admin
    assert abs(result["IS_006"] - revenue * 0.03) < 0.01  # R&D
    assert abs(result["IS_003"] - revenue * 0.015) < 0.01  # Tax surcharges


def test_is_net_profit_positive():
    result = compute_income_statement(HISTORICAL, ASSUMPTIONS)
    assert result["IS_300"] > 0
    # Net profit = total profit - tax
    assert abs(result["IS_300"] - (result["IS_200"] - result["IS_201"])) < 0.01


def test_is_operating_profit_formula():
    result = compute_income_statement(HISTORICAL, ASSUMPTIONS)
    expected_op = (
        result["IS_001"]
        - result["IS_002"]
        - result["IS_003"]
        - result["IS_004"]
        - result["IS_005"]
        - result["IS_006"]
        - result["IS_007"]
        + result.get("IS_010", 0)
        + result.get("IS_011", 0)
        + result.get("IS_012", 0)
        - result.get("IS_013", 0)
        - result.get("IS_014", 0)
        + result.get("IS_015", 0)
    )
    assert abs(result["IS_100"] - expected_op) < 0.01


# ── Balance Sheet tests ──────────────────────────────────────


def test_bs_ar_from_dso():
    is_data = compute_income_statement(HISTORICAL, ASSUMPTIONS)
    bs = compute_balance_sheet(HISTORICAL, is_data, ASSUMPTIONS)
    expected_ar = is_data["IS_001"] / 365 * 60
    assert abs(bs["BS_A_004"] - expected_ar) < 0.01


def test_bs_inventory_from_dio():
    is_data = compute_income_statement(HISTORICAL, ASSUMPTIONS)
    bs = compute_balance_sheet(HISTORICAL, is_data, ASSUMPTIONS)
    expected_inv = is_data["IS_002"] / 365 * 45
    assert abs(bs["BS_A_008"] - expected_inv) < 0.01


def test_bs_ap_from_dpo():
    is_data = compute_income_statement(HISTORICAL, ASSUMPTIONS)
    bs = compute_balance_sheet(HISTORICAL, is_data, ASSUMPTIONS)
    expected_ap = is_data["IS_002"] / 365 * 30
    assert abs(bs["BS_L_004"] - expected_ap) < 0.01


def test_bs_ppe_depreciation():
    is_data = compute_income_statement(HISTORICAL, ASSUMPTIONS)
    bs = compute_balance_sheet(HISTORICAL, is_data, ASSUMPTIONS)
    capex = is_data["IS_001"] * 0.05
    depreciation = HISTORICAL["BS_A_204"] * 0.10
    expected_ppe = HISTORICAL["BS_A_204"] + capex - depreciation
    assert abs(bs["BS_A_204"] - expected_ppe) < 0.01


def test_bs_retained_earnings():
    is_data = compute_income_statement(HISTORICAL, ASSUMPTIONS)
    bs = compute_balance_sheet(HISTORICAL, is_data, ASSUMPTIONS)
    net_profit = is_data["IS_300"]
    dividends = max(0, net_profit) * 0.30
    surplus_add = max(0, net_profit) * 0.10
    expected_re = HISTORICAL["BS_E_005"] + net_profit - dividends - surplus_add
    assert abs(bs["BS_E_005"] - expected_re) < 0.01


# ── Auto-balancer tests ──────────────────────────────────────


def test_auto_balance_achieves_balance():
    is_data = compute_income_statement(HISTORICAL, ASSUMPTIONS)
    bs = compute_balance_sheet(HISTORICAL, is_data, ASSUMPTIONS)
    balanced = auto_balance(bs)
    total_assets = balanced["BS_A_999"]
    total_le = balanced["BS_999"]
    assert abs(total_assets - total_le) < 0.01


# ── Full engine integration tests ────────────────────────────


def test_full_engine_one_year():
    engine = ForecastEngine(
        historical_data=HISTORICAL,
        assumptions={(2025, k): v for k, v in ASSUMPTIONS.items()},
        forecast_years=[2025],
    )
    result = engine.run()

    assert 2025 in result
    assert "IS" in result[2025]
    assert "BS" in result[2025]
    assert "CF" in result[2025]

    bs = result[2025]["BS"]
    cf = result[2025]["CF"]

    # BS must balance
    assert abs(bs["BS_A_999"] - bs["BS_999"]) < 0.01

    # CF closing cash = BS cash
    assert abs(cf["CF_999"] - bs["BS_A_001"]) < 0.01


def test_full_engine_three_years():
    assumptions = {}
    for year in [2025, 2026, 2027]:
        for k, v in ASSUMPTIONS.items():
            assumptions[(year, k)] = v

    engine = ForecastEngine(
        historical_data=HISTORICAL,
        assumptions=assumptions,
        forecast_years=[2025, 2026, 2027],
    )
    result = engine.run()

    for year in [2025, 2026, 2027]:
        bs = result[year]["BS"]
        cf = result[year]["CF"]

        # BS must balance each year
        assert abs(bs["BS_A_999"] - bs["BS_999"]) < 0.01, (
            f"BS imbalance in {year}: {bs['BS_A_999']:.2f} vs {bs['BS_999']:.2f}"
        )

        # CF closing cash = BS cash each year
        assert abs(cf["CF_999"] - bs["BS_A_001"]) < 0.01, (
            f"Cash mismatch in {year}: CF={cf['CF_999']:.2f} vs BS={bs['BS_A_001']:.2f}"
        )

    # Revenue should grow year over year
    assert result[2025]["IS"]["IS_001"] < result[2026]["IS"]["IS_001"]
    assert result[2026]["IS"]["IS_001"] < result[2027]["IS"]["IS_001"]


def test_run_forecast_wrapper():
    """Test the convenience wrapper used by the API layer."""
    assumptions_by_year = {2025: dict(ASSUMPTIONS), 2026: dict(ASSUMPTIONS)}
    result = run_forecast(
        historical_data=HISTORICAL,
        assumptions_by_year=assumptions_by_year,
        forecast_years=[2025, 2026],
    )

    # Returns flat dicts (no IS/BS/CF nesting)
    assert "IS_001" in result[2025]
    assert "BS_A_999" in result[2025]
    assert "CF_999" in result[2025]

    # BS balance check
    for year in [2025, 2026]:
        assert abs(result[year]["BS_A_999"] - result[year]["BS_999"]) < 0.01


def test_negative_profit_handling():
    """When net profit is negative, dividends and surplus reserve should be zero."""
    bad_assumptions = dict(ASSUMPTIONS)
    bad_assumptions["gross_margin"] = 5.0  # Very low margin → likely loss

    engine = ForecastEngine(
        historical_data=HISTORICAL,
        assumptions={(2025, k): v for k, v in bad_assumptions.items()},
        forecast_years=[2025],
    )
    result = engine.run()

    bs = result[2025]["BS"]
    # BS still balances even with a loss
    assert abs(bs["BS_A_999"] - bs["BS_999"]) < 0.01
