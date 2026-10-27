"""Allowed, denied and deferred losses preserve positive recognition and never deposit savings."""

from decimal import Decimal

import pytest
from drilling_cases import change, short

from wealthlab.household.projection import project
from wealthlab.products.drilling_example_terms import timing


@pytest.mark.parametrize(
    "choice,agi", [("allowed", -60000), ("denied", 20000), ("deferred", 20000)]
)
def test_independent_federal_loss_timing_keeps_actual_cash_and_positive_exit_gain(choice, agi):
    def configure(data):
        for item in data["drilling_plan"]["observations"][0]["deductions"]:
            item["federal_timing"] = timing(choice)

    row = project(change(short(), configure))[0]
    assert row["annual_tax"]["federal"]["agi"] == agi
    assert row["drilling_federal_ordinary_recapture"] == 20000
    assert (row["closing_cash"], row["tax_event_cash"]) == (140000, 0)
    if choice == "deferred":
        events = row["drilling_audit"]["future_tax_events"]
        assert (
            sum(Decimal(e["federal"]["allowed_nonpassive_partnership_income"]) for e in events)
            == -80000
        )


def test_released_loss_on_later_month_is_applied_once_after_earlier_economic_exit():
    def configure(data):
        plan = data["drilling_plan"]
        first, last = plan["observations"]
        first.update(exit_requested=True, exit_gross_proceeds="40000")
        for item in first["deductions"]:
            item["federal_timing"] = dict(
                treatment="deferred", release_on="2026-02-28", eligibility_after_limits_assumed=True
            )
        for key in (
            "production_units",
            "operating_cost",
            "residual_property_value",
            "distribution_request",
        ):
            last[key] = "0"
        last["deductions"] = []
        last["exit_requested"] = False

    rows = project(change(short(2), configure))
    assert rows[0]["annual_tax"]["federal"]["agi"] == 20000
    assert rows[1]["annual_tax"]["federal"]["agi"] == -60000
    assert rows[1]["drilling_audit"]["future_tax_events"] == []
    assert rows[1]["closing_cash"] == 140000
