"""Forecast limits decide sales; an estimated bonus never becomes actual income or cash."""

from decimal import Decimal

from tests.household_budget_cases import synthetic
from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario


def test_budget_sale_sweeps_actual_proceeds_once_and_keeps_original_inputs():
    case = synthetic()
    original = case.model_dump_json()
    rows = project(case)
    sale = rows[-1]["lot_audit"]["sale_decisions"][0]
    assert case.model_dump_json() == original
    assert Decimal("49.7") < sale["sold_units"] < Decimal("49.9")
    assert sale["estimated_incremental_liability"] == 500
    assert sale["budget_met_is_estimate"]
    # $1,000 cash +$4,976.18 actual proceeds, with remaining shares $5,023.82.
    assert rows[-1]["closing_cash"] == Decimal("5976.18")
    assert rows[-1]["net_wealth"] == 11000


def test_estimate_is_not_actual_income_tax_payment_or_saving():
    rows = project(synthetic())
    final = rows[-1]
    audit = final["lot_audit"]["budget_audit"][0]
    # Only the realized $50/share federal basis difference enters AGI; the
    # forecast $200k bonus never arrives. Both actual taxes are below thresholds.
    assert final["annual_tax"]["federal"]["agi"] == Decimal("2488.09")
    assert (audit["estimated_delta_at_decision"], audit["estimate_after_observed_trades"]) == (
        500,
        500,
    )
    assert audit["actual_total_liability"] == audit["actual_net_cash_tax_paid"] == 0
    assert audit["actual_return_status"] == "closed"


def test_repeated_policy_cannot_spend_the_same_cumulative_annual_budget_again():
    data = synthetic().model_dump(mode="json")
    first = data["lot_plan"]["case"]["sale_policies"][0]
    data["lot_plan"]["case"]["sale_policies"].append(dict(first, id="second", date="2026-02-28"))
    final = project(Scenario.model_validate(data))[-1]
    first, second = final["lot_audit"]["sale_decisions"]
    assert second["sold_units"] < Decimal(".001")
    assert (
        first["estimated_incremental_liability"] == second["estimated_incremental_liability"] == 500
    )
    assert final["lot_audit"]["budget_audit"][-1]["estimate_after_observed_trades"] == 500


def test_policy_commission_is_paid_once_without_depositing_forecast_tax_savings():
    data = synthetic().model_dump(mode="json")
    data["lot_plan"]["case"]["sale_policies"][0]["commission"] = "1"
    final = project(Scenario.model_validate(data))[-1]
    assert final["net_wealth"] == 10999
    assert final["lot_audit"]["budget_audit"][0]["actual_net_cash_tax_paid"] == 0
    assert sum(Decimal(trade["commission"]) for trade in final["lot_audit"]["trades"]) == 1
