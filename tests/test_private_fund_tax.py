"""Federal/state losses remain independently conditional at an actual complete cash exit."""

import pytest
from private_fund_cases import fund, request

from wealthlab.household.projection import project


@pytest.mark.parametrize("treatment,agi", [("allowed", -3000), ("denied", 0), ("deferred", 0)])
def test_exit_uses_actual_cash_independent_basis_and_conditional_federal_loss(treatment, agi):
    choice = dict(
        treatment=treatment,
        eligibility_after_limits_assumed=True,
        release_on="2027-01-31" if treatment == "deferred" else None,
    )
    case = fund(
        federal_opening_basis="120000",
        new_jersey_opening_basis="80000",
        federal_exit_loss=choice,
        requests=[request(final=True)],
    )
    rows = project(case)
    last = rows[-1]
    assert last["annual_tax"]["federal"]["agi"] == agi
    assert last["annual_tax"]["new_jersey"]["gross_income"] == 20000
    assert last["sleeve_audit"][-1]["fund_basis"] == dict(federal=0, new_jersey=0)
    assert last["net_wealth"] == 110000 - last["annual_tax"]["total_liability"]
    assert sum(r["tax_event_cash"] for r in rows) == 0


def test_basis_adjustments_are_separate_from_deductibility_and_create_no_cash():
    adjustment = dict(
        id="basis_item",
        provenance="assumption",
        date="2026-01-15",
        federal="-12000",
        new_jersey="-5000",
        explanation="Independent supplied basis",
    )
    rows = project(fund(basis_adjustments=[adjustment], requests=[request(final=True)]))
    last = rows[-1]
    assert last["annual_tax"]["federal"]["agi"] == 12000
    assert last["annual_tax"]["new_jersey"]["gross_income"] == 5000
    assert rows[0]["sleeve_redemptions"] == 100000
    assert last["net_wealth"] == 110000 - last["annual_tax"]["total_liability"]
