"""Only cash actually received can fund an IRA request; no later backfilling."""

from decimal import Decimal

from tests.ira_deposit_household_cases import one_year
from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario


def test_current_ira_withdrawal_cash_is_available_for_a_confirmed_contribution():
    data = one_year().model_dump(mode="json")
    data["accounts"][0]["balance"] = "0"
    data["incomes"][0]["start"] = "2026-02-01"
    rows = project(Scenario.model_validate(data))
    assert rows[0]["ira_withdrawal_cash"] == 20000
    assert rows[0]["ira_contributions"] == 3000
    assert rows[0]["income"] == 0


def test_later_pay_does_not_retry_unfunded_january_deposit():
    data = one_year().model_dump(mode="json")
    data["accounts"][0]["balance"] = "0"
    data["incomes"][0]["start"] = "2026-02-01"
    data["ira_plan"]["orders"] = []
    rows = project(Scenario.model_validate(data))
    assert (rows[0]["ira_contributions"], rows[0]["ira_contributions_unfilled"]) == (0, 3000)
    assert sum(r["ira_contributions"] for r in rows) == 3000
    assert rows[-1]["ira_annual_reconciliation"]["owners"][0]["nj_ira_basis"] == 0


def test_household_tax_events_are_not_replayed_by_the_receipt_hook():
    data = one_year().model_dump(mode="json")
    data["tax_plan"]["events"] = [
        dict(
            date="2026-03-15",
            description="One supplied interest receipt",
            cash_received="1000",
            federal=dict(interest="1000"),
            new_jersey=dict(interest="1000"),
        )
    ]
    baseline = project(one_year())
    rows = project(Scenario.model_validate(data))
    assert sum(r["tax_event_cash"] for r in rows) - sum(
        r["tax_event_cash"] for r in baseline
    ) == Decimal(1000)
    assert rows[-1]["ira_contribution_eligibility"]["traditional_ira_magi"] == 91000
