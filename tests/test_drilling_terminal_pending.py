"""Executed property closure and actual liquid-book closure retain different obligations."""

from drilling_cases import change, short
from test_drilling_terminal_state import terminal


def test_closed_property_can_still_have_unrecognized_future_tax_facts():
    def edit(data):
        for deduction in data["drilling_plan"]["observations"][0]["deductions"]:
            deduction["federal_timing"] = dict(
                treatment="deferred", release_on="2026-03-31", eligibility_after_limits_assumed=True
            )

    audit = terminal(change(short(), edit))
    assert audit["terminal_state"]["closed"] is True
    assert audit["terminal_state"]["property_sold"] is True
    assert audit["future_tax_events"]


def test_reference_exposes_its_actual_empty_book_without_fabricating_a_property_sale():
    case = change(short(), lambda data: data["drilling_plan"].update(mode="liquid_reference"))
    audit = terminal(case)
    state = audit["terminal_state"]
    assert state["mode"] == "liquid_reference"
    assert (state["closed"], state["property_sold"]) == (False, False)
    assert audit["reference_lots"] == []
    assert state["reference_cash"] == {case.drilling_plan.account_id: 0}
    assert state["reference_exit_pending"] is False
    assert state["reference_pending_losses"] == {"federal": 0, "nj": 0}
