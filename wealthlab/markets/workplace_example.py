"""Synthetic payroll-funded pretax/Roth accounts use one confirmed month-end factor proxy."""

from wealthlab.markets.example import asset
from wealthlab.markets.household_example import selected_mode
from wealthlab.markets.household_inputs import HouseholdBinding
from wealthlab.markets.inputs import MarketCase
from wealthlab.markets.wrapper_example import wrapper
from wealthlab.retirement.workplace_example import synthetic as workplace


def synthetic(mode="deterministic", stress="early_crash"):
    household = workplace()
    market = MarketCase.model_validate(
        dict(
            start=household.start,
            end=household.end,
            mode="monte_carlo" if mode == "monte_carlo" else "deterministic",
            assets=[asset("portfolio", "equity", 0.04, 0.15, 0.02)],
            return_convention="price_plus_cash",
            expected_annual_inflation=0.025,
            annual_inflation_volatility=0.015,
            correlation=[[1, 0.1], [0.1, 1]],
            seed=42,
            paths=8 if mode == "monte_carlo" else 1,
        )
    )
    if mode == "historical":
        from wealthlab.markets.wrapper_example import synthetic as ira_example

        _, other, _ = ira_example(mode)
        history = other.historical.model_dump(mode="json")
        history["months"] = history["months"][:12]
        market = MarketCase.model_validate(
            dict(market.model_dump(mode="json"), mode=mode, historical=history)
        )
    elif mode == "stress":
        market = selected_mode(market, mode, stress)
    binding = HouseholdBinding.model_validate(
        dict(
            wrappers=[wrapper(account) for account in household.workplace_plan.products],
            cash_yield_timing="opening_value_received_before_month_end_sales",
            ordinary_cash_character_confirmed=True,
            other_accounts_unmodeled_returns_confirmed=True,
        )
    )
    return household, market, binding
