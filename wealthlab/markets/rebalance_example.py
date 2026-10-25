"""Synthetic equity/bond reallocation and an otherwise identical hold control.

Both strategies retain identical funding permissions and account opening values.
Invented historical observations are trimmed to the same two-year horizon; they
are a reproducible demonstration, not evidence of actual investment performance.
"""

from wealthlab.household.scenario import Scenario
from wealthlab.markets.example import synthetic as market_example
from wealthlab.markets.household_example import synthetic as household_example
from wealthlab.markets.household_inputs import HouseholdBinding
from wealthlab.markets.inputs import MarketCase
from wealthlab.markets.stresses import events


def synthetic(mode="deterministic", stress="early_crash"):
    household, _, binding = household_example()
    data = household.model_dump(mode="json")
    data["name"] = "Synthetic taxable equity/bond rebalancing"
    linked = data["lot_plan"]
    linked["case"]["securities"].append(
        dict(
            id="bond",
            provenance="illustration",
            kind="etf",
            wash_group="bond",
            exposure_group="bond",
        )
    )
    linked["opening_prices"]["bond"] = "100"
    linked["case"]["closing_prices"]["bond"] = "100"
    for marks in linked["monthly_marks"]:
        marks["prices"]["bond"] = "100"
    linked["funding_sources"].append(
        dict(account_id="brokerage", security_id="bond", selection="hifo", commission="1")
    )
    linked["rebalances"] = [
        policy(i, marks["date"]) for i, marks in enumerate(linked["monthly_marks"]) if i % 3 == 0
    ]
    bindings = binding.model_dump(mode="json")
    bindings["securities"].append(
        dict(
            security_id="bond",
            factor="bonds",
            federal_cash_character="interest",
            nj_cash_character="interest",
        )
    )
    return (
        Scenario.model_validate(data),
        market(data, mode, stress),
        HouseholdBinding.model_validate(bindings),
    )


def policy(index, when):
    return dict(
        id=f"rebalance_{index}",
        provenance="illustration",
        date=when,
        account_id="brokerage",
        target_weights=dict(stock=".5", bond=".5"),
        drift_band=".05",
        max_sale_fraction=".5",
        selection="hifo",
        commission_per_trade="1",
        funding="sale_proceeds_only",
    )


def market(household, mode, stress):
    data = market_example("historical" if mode == "historical" else "deterministic").model_dump(
        mode="json"
    )
    data.update(
        start=household["start"],
        end=household["end"],
        assets=data["assets"][:2],
        correlation=[[1, -0.1, 0.1], [-0.1, 1, -0.2], [0.1, -0.2, 1]],
        paths=8 if mode == "monte_carlo" else 1,
    )
    if mode == "historical":
        history = data["historical"]
        history["retrieved_on"] = "2010-01-01"
        history["source"] += "; retrieval and availability dates are synthetic assumptions"
        history["months"] = [
            dict(
                row,
                mark_returns={k: row["mark_returns"][k] for k in ("equities", "bonds")},
                cash_yields={k: row["cash_yields"][k] for k in ("equities", "bonds")},
            )
            for row in history["months"][:24]
        ]
    if mode == "stress":
        data["shocks"] = events(MarketCase.model_validate(data), stress)
    data["mode"] = mode
    return MarketCase.model_validate(data)


def hold(scenario):
    return scenario.model_copy(
        update=dict(lot_plan=scenario.lot_plan.model_copy(update=dict(rebalances=[])))
    )
