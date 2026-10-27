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
