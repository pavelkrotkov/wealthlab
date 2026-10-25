"""Synthetic liquid saving keeps its shares, current bills and cash buffer distinct."""

from wealthlab.household.scenario import Scenario
from wealthlab.portfolio.household_example import plan
from wealthlab.products.life_household_example import synthetic as policy_household


def synthetic():
    data = policy_household().model_dump(mode="json")
    data.update(name="Synthetic scheduled liquid saving", life_plan=None)
    data["accounts"] = [data["accounts"][0]]
    data["accounts"][0]["balance"] = "5000"
    data["accounts"].append(
        dict(
            id="brokerage",
            provenance="assumption",
            owner="person_a",
            currency="USD",
            wrapper="taxable",
            balance="0",
            monthly_fee="0",
        )
    )
    lots = plan(Scenario.model_validate(data))
    lots["case"]["lots"] = []
    lots["case"]["closing_prices"]["stock"] = "100"
    lots["funding_sources"] = []
    lots["savings"] = [
        dict(
            id=f"saving_{i}",
            provenance="assumption",
            date=mark["date"],
            account_id="brokerage",
            amount="500",
            target_weights={"stock": "1"},
            commission_per_trade="0",
            minimum_cash="0",
        )
        for i, mark in enumerate(lots["monthly_marks"])
    ]
    data["lot_plan"] = lots
    return Scenario.model_validate(data)
