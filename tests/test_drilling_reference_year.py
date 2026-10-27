"""A December share loss stays in its sale year; unresolved forward buys block settlement."""

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.products.drilling_example import synthetic
from wealthlab.products.drilling_reporting import annual_returns


def december_loss(future_buy=False):
    data = synthetic().model_dump(mode="json")
    plan = data["drilling_plan"]
    plan["mode"] = "liquid_reference"
    for i, row in enumerate(plan["observations"]):
        row.update(
            reference_cash_request="0",
            exit_requested=i == 11,
            reference_price="100" if i < 11 else "90",
        )
    if future_buy:
        plan["observations"][12]["capital_call"] = "100"
    return Scenario.model_validate(data)


def test_december_loss_reconciles_in_sale_year_despite_forward_window_ending_january():
    rows = project(december_loss())
    federal = annual_returns(rows)["2026"]["federal"]
    assert (federal["agi"], federal["short_carry"]) == (117000, 7000)
    assert rows[11]["drilling_exit_cash"] == 90000
    assert rows[-1]["drilling_audit"]["reference_disposals"]


def test_january_month_end_buy_is_outside_december_thirty_day_window():
    rows = project(december_loss(True))
    assert annual_returns(rows)["2026"]["federal"]["short_carry"] == 7000
    assert rows[12]["drilling_call_funded"] == 100
