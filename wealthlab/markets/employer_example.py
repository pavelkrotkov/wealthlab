"""Synthetic employer account: supplied tax allocations remain independent of market marks."""

from wealthlab.employment.compensation_example import synthetic as compensation
from wealthlab.household.scenario import Scenario
from wealthlab.markets.example import asset
from wealthlab.markets.household_example import selected_mode
from wealthlab.markets.household_inputs import HouseholdBinding
from wealthlab.markets.inputs import MarketCase


def synthetic(mode="deterministic", stress="early_crash"):
    data = compensation().model_dump(mode="json")
    data["name"] = "Synthetic employer market and employment linkage"
    household = Scenario.model_validate(data)
    market = MarketCase.model_validate(
        dict(
            start=data["start"],
            end=data["end"],
            mode="monte_carlo" if mode == "monte_carlo" else "deterministic",
            assets=[asset("employer", "employer", 0.04, 0.35, 0)],
            return_convention="price_plus_cash",
            expected_annual_inflation=0.025,
            annual_inflation_volatility=0.015,
            correlation=[[1, 0.1], [0.1, 1]],
            seed=42,
            paths=8 if mode == "monte_carlo" else 1,
        )
    )
    if mode == "historical":
        market = history(market)
    elif mode == "stress":
        market = selected_mode(market, mode, stress)
    binding = HouseholdBinding.model_validate(
        dict(
            employers=[
                dict(
                    account_id="employer_fund",
                    factor="employer",
                    return_convention="net_mark_return_no_separate_cash_yield",
                    replace_entered_net_returns_confirmed=True,
                    event_sequence_start=90000,
                    employment=dict(
                        path_id="job_policy",
                        drawdown_trigger=".3",
                        months_out=6,
                        return_multiplier=".5",
                        forfeit_remaining_unvested=True,
                        replace_future_work_changes_confirmed=True,
                    ),
                )
            ],
            cash_yield_timing="opening_value_received_before_month_end_sales",
            ordinary_cash_character_confirmed=True,
            other_accounts_unmodeled_returns_confirmed=True,
        )
    )
    return household, market, binding


def history(case):
    from wealthlab.markets.household_example import synthetic as taxable

    _, example, _ = taxable("historical")
    source = example.historical.model_dump(mode="json")
    for row in source["months"]:
        row["mark_returns"] = dict(employer=row["mark_returns"]["equities"])
        row["cash_yields"] = dict(employer=0)
    return MarketCase.model_validate(
        dict(case.model_dump(mode="json"), mode="historical", historical=source)
    )
