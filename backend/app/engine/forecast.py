"""
Three-Statement Forecast Engine

Orchestrates the iterative computation of Income Statement, Balance Sheet,
and Cash Flow Statement across multiple forecast years. The three statements
are linked: IS feeds BS, BS feeds CF, CF closing cash writes back to BS,
and updated debt on BS feeds back to IS finance costs.

The engine iterates until the balance sheet / cash flow converge
(change in closing cash < 0.01, max 10 rounds per year).

Pure functions throughout — dict in, dict out, no database access.
"""

from __future__ import annotations

from app.engine.balance_sheet import compute_balance_sheet, recalculate_bs_subtotals
from app.engine.balancer import auto_balance
from app.engine.cash_flow import compute_cash_flow
from app.engine.income_statement import compute_income_statement


_MAX_ITERATIONS = 10
_CONVERGENCE_THRESHOLD = 0.01


class ForecastEngine:
    """Three-statement financial forecast engine with iterative balancing.

    Usage::

        engine = ForecastEngine(
            historical_data={"IS_001": 100_000, "BS_A_001": 20_000, ...},
            assumptions={(2025, "revenue_growth_rate"): 10.0, ...},
            forecast_years=[2025, 2026, 2027],
        )
        results = engine.run()
        # results[2025]["IS"]["IS_001"] == 110_000

    Args:
        historical_data: Last historical year's data, mapping
            line_item_code -> float.
        assumptions: Per-year assumptions, mapping
            (year, param_key) -> float.
        forecast_years: Ordered list of years to project.
        prior_year_data: If provided, used as "prior" for the first forecast
            year instead of *historical_data*. Useful when the caller already
            has the year-before-forecast data separated out.
    """

    def __init__(
        self,
        historical_data: dict[str, float],
        assumptions: dict[tuple[int, str], float],
        forecast_years: list[int],
        prior_year_data: dict[str, float] | None = None,
    ) -> None:
        self.historical_data = dict(historical_data)
        self.assumptions = dict(assumptions)
        self.forecast_years = list(forecast_years)
        self.prior_year_data = dict(prior_year_data) if prior_year_data else None

    # ── Public API ────────────────────────────────────────────

    def run(self) -> dict[int, dict[str, dict[str, float]]]:
        """Execute the forecast and return results for every projected year.

        Returns:
            ``{year: {"IS": {...}, "BS": {...}, "CF": {...}}}``
        """
        results: dict[int, dict[str, dict[str, float]]] = {}

        for year in self.forecast_years:
            prior = self._get_prior(year, results)
            year_assumptions = self._get_year_assumptions(year)

            is_data, bs_data, cf_data = self._compute_year(
                prior, year_assumptions
            )

            results[year] = {
                "IS": is_data,
                "BS": bs_data,
                "CF": cf_data,
            }

        return results

    # ── Per-year computation with iterative convergence ───────

    def _compute_year(
        self,
        prior: dict[str, float],
        assumptions: dict[str, float],
    ) -> tuple[dict[str, float], dict[str, float], dict[str, float]]:
        """Run the iterative three-statement loop for one forecast year.

        Each iteration:
            1. Compute IS (interest depends on debt from prior iteration)
            2. Compute BS (equity depends on NP; cash carried from prior year)
            3. Compute CF (indirect method; derives closing cash)
            4. Write CF closing cash back to BS and recalculate subtotals
            5. Auto-balance BS via debt plug if needed (handles unbalanced input)
            6. Check convergence (closing cash stabilises)

        The outer loop converges the interest <-> debt circular reference.

        Returns (is_data, bs_data, cf_data) after convergence.
        """
        prior_bs = {k: v for k, v in prior.items() if k.startswith("BS_")}
        current_bs_for_interest: dict[str, float] | None = None
        previous_cash = float("inf")

        is_data: dict[str, float] = {}
        bs_data: dict[str, float] = {}
        cf_data: dict[str, float] = {}

        for _ in range(_MAX_ITERATIONS):
            # 1. Income Statement
            is_data = compute_income_statement(
                prior, assumptions, current_bs=current_bs_for_interest
            )

            # 2. Balance Sheet
            bs_data = compute_balance_sheet(prior, is_data, assumptions)

            # 3. Cash Flow Statement
            cf_data = compute_cash_flow(
                prior, is_data, bs_data, prior_bs, assumptions
            )

            # 4. Write closing cash back to BS
            bs_data["BS_A_001"] = cf_data["CF_999"]
            recalculate_bs_subtotals(bs_data)

            # 5. Auto-balance (debt plug for any residual gap)
            bs_data = auto_balance(bs_data)

            # 6. Convergence check
            current_cash = cf_data["CF_999"]
            if abs(current_cash - previous_cash) < _CONVERGENCE_THRESHOLD:
                break
            previous_cash = current_cash

            # Feed back the balanced BS for interest recalculation
            current_bs_for_interest = bs_data

        return is_data, bs_data, cf_data

    # ── Helpers ───────────────────────────────────────────────

    def _get_prior(
        self,
        year: int,
        results: dict[int, dict[str, dict[str, float]]],
    ) -> dict[str, float]:
        """Build the flat prior-year data dict for *year*.

        For the first forecast year this comes from historical / prior_year_data.
        For subsequent years it is flattened from the previous year's output.
        """
        prev_year = year - 1
        if prev_year in results:
            return _flatten_year(results[prev_year])

        # First forecast year
        if self.prior_year_data is not None:
            return dict(self.prior_year_data)
        return dict(self.historical_data)

    def _get_year_assumptions(self, year: int) -> dict[str, float]:
        """Extract the assumption dict for a specific *year*."""
        return {
            param_key: value
            for (y, param_key), value in self.assumptions.items()
            if y == year
        }


def _flatten_year(year_data: dict[str, dict[str, float]]) -> dict[str, float]:
    """Merge IS / BS / CF sub-dicts into a single flat dict."""
    flat: dict[str, float] = {}
    for statement_dict in year_data.values():
        flat.update(statement_dict)
    return flat


def run_forecast(
    historical_data: dict[str, float],
    assumptions_by_year: dict[int, dict[str, float]],
    forecast_years: list[int],
) -> dict[int, dict[str, float]]:
    """Convenience wrapper for the API layer.

    Accepts assumptions as ``{year: {param_key: value}}`` and returns
    a flat ``{year: {line_item_code: value}}`` dict (no IS/BS/CF nesting).
    """
    # Convert {year: {key: val}} → {(year, key): val}
    assumptions: dict[tuple[int, str], float] = {}
    for year, params in assumptions_by_year.items():
        for key, val in params.items():
            assumptions[(year, key)] = val

    engine = ForecastEngine(
        historical_data=historical_data,
        assumptions=assumptions,
        forecast_years=forecast_years,
    )
    nested = engine.run()

    # Flatten each year's IS/BS/CF into a single dict
    return {year: _flatten_year(data) for year, data in nested.items()}
