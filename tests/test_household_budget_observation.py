"""Only observed trades/marks and already-available forecast snapshots may influence a sale."""

from copy import deepcopy

import pytest

from tests.household_budget_cases import synthetic
from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario


def first_decision(data):
    return project(Scenario.model_validate(data))[-1]["lot_audit"]["sale_decisions"][0]


@pytest.mark.parametrize("future", ["prices", "trade", "income"])
def test_future_actual_price_trade_or_income_does_not_choose_earlier_sale(future):
    data = synthetic().model_dump(mode="json")
    before = first_decision(data)
    if future == "prices":
        for mark in data["lot_plan"]["monthly_marks"][1:]:
            mark["prices"]["stock"] = "300"
        data["lot_plan"]["case"]["closing_prices"]["stock"] = "300"
    elif future == "trade":
        data["lot_plan"]["case"]["trades"] = [
            dict(
                id="future",
                provenance="illustration",
                date="2026-06-30",
                action="sell",
                account_id="brokerage",
                security_id="stock",
                quantity="10",
                price="250",
                commission="0",
            )
        ]
    else:
        data["tax_plan"]["events"].append(
            dict(
                date="2026-06-01",
                description="Actual later hypothetical bonus",
                cash_received="100000",
                federal=dict(wages_primary="100000"),
                new_jersey=dict(wages="100000"),
            )
        )
    assert first_decision(data) == before


def test_future_dated_forecast_revision_changes_only_later_decisions():
    data = synthetic().model_dump(mode="json")
    before = first_decision(data)
    later = deepcopy(data["lot_plan"]["tax_budget_forecasts"][0])
    later.update(id="july_revision", source_date="2026-07-01", available_on="2026-07-01")
    later["cases"][0]["federal_income"]["wages_primary"] = "100000"
    later["cases"][0]["nj_income"]["wages"] = "100000"
    data["lot_plan"]["tax_budget_forecasts"].append(later)
    first = data["lot_plan"]["case"]["sale_policies"][0]
    data["lot_plan"]["case"]["sale_policies"].append(dict(first, id="august", date="2026-08-31"))
    decisions = project(Scenario.model_validate(data))[-1]["lot_audit"]["sale_decisions"]
    assert decisions[0] == before
    assert decisions[1]["forecast_id"] == "july_revision"
    assert decisions[1]["sold_units"] > 50
