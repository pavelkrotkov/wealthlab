"""A synthetic actual-lot household reuses the same seeded price and cash-yield paths."""

from wealthlab.household.scenario import Scenario
from wealthlab.markets.example import asset, invented_history
from wealthlab.markets.household_inputs import HouseholdBinding
from wealthlab.markets.inputs import MarketCase
from wealthlab.markets.stresses import events
from wealthlab.portfolio.household_example import synthetic as lots


def synthetic(mode="deterministic", stress="early_crash"):
    data = lots().model_dump(mode="json")
    data["name"] = "Synthetic actual household market-path funding"
    data["lot_plan"]["year_end_wash_policy"] = "january_reconcile"
    data["lot_plan"]["post_horizon_purchases"] = "none_for_30_days"
    household = Scenario.model_validate(data)
    market = MarketCase.model_validate(
        dict(
            start=data["start"],
            end=data["end"],
            mode="deterministic" if mode in {"historical", "stress"} else mode,
            assets=[asset("equities", "equity", 0.05, 0.18, 0.02)],
            return_convention="price_plus_cash",
            expected_annual_inflation=0.025,
            annual_inflation_volatility=0.015,
            correlation=[[1, 0.1], [0.1, 1]],
            seed=42,
            paths=8 if mode == "monte_carlo" else 1,
        )
    )
    market = selected_mode(market, mode, stress)
    binding = HouseholdBinding.model_validate(
        dict(
            securities=[
                dict(
                    security_id="stock",
                    factor="equities",
                    federal_cash_character="dividends",
                    nj_cash_character="dividends",
                )
            ],
            inflation_expenses=[],
            cash_yield_timing="opening_value_received_before_month_end_sales",
            ordinary_cash_character_confirmed=True,
            other_accounts_unmodeled_returns_confirmed=True,
        )
    )
    return household, market, binding


def selected_mode(case, mode, stress):
    data = case.model_dump(mode="json")
    if mode == "historical":
        history = invented_history()
        history["retrieved_on"] = "2010-01-01"
        history["source"] += "; retrieval/availability dates are synthetic assumptions"
        history["months"] = [
            dict(
                row,
                mark_returns=dict(equities=row["mark_returns"]["equities"]),
                cash_yields=dict(equities=row["cash_yields"]["equities"]),
            )
            for row in history["months"][:24]
        ]
        data.update(mode=mode, historical=history)
    if mode == "stress":
        data.update(mode=mode, shocks=events(case, stress))
    return MarketCase.model_validate(data)
