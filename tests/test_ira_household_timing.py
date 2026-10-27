"""Cash chronology and completed annual IRA tax reconciliation stay distinct."""

from wealthlab.household.projection import project
from wealthlab.retirement.ira_household_example import synthetic


def test_annual_income_enters_december_without_redepositing_cash():
    rows = project(synthetic())
    assert rows[10]["annual_tax"]["total_liability"] == 0
    assert rows[11]["annual_tax"]["total_liability"] == 2420
    assert rows[23]["annual_tax"]["total_liability"] == 2000
    assert rows[6]["ira_conversion_value"] == 10000
    assert rows[6]["ira_withdrawal_cash"] == 0
    assert rows[11]["tax_event_cash"] == 0
