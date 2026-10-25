"""Native tax-budget decisions retain forecasts while optimizer exits spend only actual cash."""

from decimal import Decimal

import pytest
from optimization_cases import flat

from tests.household_budget_cases import two_year
from wealthlab.optimization.inputs import PolicySearch
from wealthlab.optimization.search import search


@pytest.fixture(scope="module")
def result():
    household = two_year()
    budget = household.lot_plan.case.sale_policies[0].model_dump(mode="json")
    exit_policy = dict(budget, id="exit", date="2027-12-31", mode="sell_all", tax_budget=None)
    data = flat().model_dump(mode="json")
    data["household"] = household.model_dump(mode="json")
    for market in (data["training"], data["validation"]):
        market.update(start=str(household.start), end=str(household.end))
    data["targets"].update(reserve_years=0, maximum_issuer_weight=None)
    data["dimensions"] = [
        dict(
            id="sale_timing",
            choices=[
                dict(id="budget_then_exit", sale_policies=[budget, exit_policy]),
                dict(id="terminal_only", sale_policies=[exit_policy]),
            ],
        )
    ]
    return search(PolicySearch.model_validate(data))


def test_budget_and_terminal_only_choices_share_capital_and_actual_tax_cash(result):
    assert [c["median_real_after_tax_exit_wealth"] for c in result["candidates"]] == [11000] * 2
    assert result["held_out"]["assessment"]["median_real_after_tax_exit_wealth"] == 11000
    assert result["configured_validation_passed"]


def test_estimate_retains_actual_years_and_never_creates_bonus_or_tax_saving_cash(result):
    rows = result["selected_training"]["details"][0]["rows"]
    final = rows[-1]
    first_sale = final["lot_audit"]["sale_decisions"][0]
    assert first_sale["estimated_incremental_liability"] == 500
    assert Decimal("49.7") < first_sale["sold_units"] < Decimal("49.9")
    assert final["closing_cash"] == final["net_wealth"] == 11000
    assert rows[11]["annual_tax"]["federal"]["agi"] == Decimal("2488.09")
    assert final["annual_tax"]["federal"]["agi"] == Decimal("2511.91")
    assert final["annual_tax"]["total_liability"] == 0
