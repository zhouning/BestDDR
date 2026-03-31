"""
Balance Sheet Auto-Balancer

In a three-statement model, cash is determined by the Cash Flow Statement.
When the balance sheet does not balance after writing back CF closing cash,
the gap is closed by adjusting short-term debt (the "debt plug").

Adjusting debt changes interest expense, which feeds back through IS -> BS ->
CF, so the caller must iterate until convergence.

Pure function — no DB access.
"""

from app.engine.balance_sheet import recalculate_bs_subtotals


def auto_balance(bs_data: dict[str, float]) -> dict[str, float]:
    """Balance the balance sheet by adjusting short-term debt only.

    In a three-statement model, cash is determined by the Cash Flow Statement.
    The balance sheet is balanced by adjusting the short-term debt plug:

        gap = total_assets - (total_liabilities + total_equity)

    The debt plug (BS_L_001) is adjusted to close the gap:
        - gap > 0 => assets exceed funding => increase BS_L_001
        - gap < 0 => funding exceeds assets => decrease BS_L_001

    Cash (BS_A_001) is NEVER adjusted here. It is always set externally
    by writing back CF_999 (the cash flow closing balance).

    Args:
        bs_data: Balance sheet dict (will be copied, not mutated).

    Returns:
        New balanced BS dict with recalculated subtotals.
    """
    bs = dict(bs_data)
    g = _safe_get

    total_assets = g(bs, "BS_A_100") + g(bs, "BS_A_300")
    total_liab_equity = g(bs, "BS_L_100") + g(bs, "BS_L_300") + g(bs, "BS_E_100")
    gap = total_assets - total_liab_equity

    if abs(gap) < 0.001:
        return bs

    # Adjust short-term debt to close the gap.
    # Negative debt is allowed as a model artifact (signals excess funding).
    bs["BS_L_001"] = g(bs, "BS_L_001") + gap

    recalculate_bs_subtotals(bs)
    return bs


def _safe_get(d: dict, key: str, default: float = 0.0) -> float:
    """Return float value from dict, defaulting to *default* if missing."""
    return float(d.get(key, default))
