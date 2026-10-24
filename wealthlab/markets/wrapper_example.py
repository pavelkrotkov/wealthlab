"""Synthetic ordinary IRA/529 proxies reuse fixed withdrawal, conversion and tuition dates."""

from wealthlab.household.scenario import Scenario
from wealthlab.markets.example import asset
from wealthlab.markets.household_example import selected_mode
from wealthlab.markets.household_inputs import HouseholdBinding
from wealthlab.markets.inputs import MarketCase
from wealthlab.retirement.education_household_example import plan as education_plan
from wealthlab.retirement.ira_household_example import synthetic as ira_household


def synthetic(mode="deterministic", stress="early_crash"):
    data = ira_household().model_dump(mode="json")
    data["name"] = "Synthetic IRA and education market proxies"
    data["accounts"].append(
        dict(
            id="college",
            provenance="illustration",
            owner="person_a",
            wrapper="education",
            currency="USD",
            balance="30000",
            monthly_fee="0",
        )
    )
    data["education_plan"] = education_plan()
    scenario = Scenario.model_validate(data)
    market = MarketCase.model_validate(
        dict(
            start=data["start"],
            end=data["end"],
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
        from wealthlab.markets.household_example import synthetic as taxable

        _, example, _ = taxable(mode)
        history = example.historical.model_dump(mode="json")
        for row in history["months"]:
            row["mark_returns"] = dict(portfolio=row["mark_returns"]["equities"])
            row["cash_yields"] = dict(portfolio=row["cash_yields"]["equities"])
        market = MarketCase.model_validate(
            dict(market.model_dump(mode="json"), mode=mode, historical=history)
        )
    elif mode == "stress":
        market = selected_mode(market, mode, stress)
    binding = HouseholdBinding.model_validate(
        dict(
            wrappers=[wrapper(account) for account in ("retirement", "roth", "college")],
            cash_yield_timing="opening_value_received_before_month_end_sales",
            ordinary_cash_character_confirmed=True,
            other_accounts_unmodeled_returns_confirmed=True,
        )
    )
    return scenario, market, binding


def wrapper(identity):
    return dict(
        account_id=identity,
        factor="portfolio",
        return_convention="mark_plus_yield_on_month_end_balance",
        liquidity_convention="block_outgoing_withdrawals_and_conversions",
        replace_entered_returns_confirmed=True,
    )
