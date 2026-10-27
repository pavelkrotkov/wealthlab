"""The interpretation affects the bill, never creates capital or a second fee liability."""

from decimal import Decimal

from tests.advisory_billing_cases import quarter
from tests.advisory_cases import change
from wealthlab.household.projection import project


def test_partial_cash_retains_one_actual_whole_base_quarter_fee_debt():
    scenario = quarter(cash="10")
    final = project(scenario)[-1]
    assert final["advisory_fees_assessed"] == 23
    assert final["advisory_fees_paid"] == 10
    assert final["closing_cash"] == 0
    assert final["account_balances"]["brokerage"] == 23000
    assert final["fees_owed"] == final["advisory_fees_owed"] == 13
    assert final["net_wealth"] == 22987
    assert final["funding_failure"] is True


def test_fixed_charge_is_added_once_after_the_supplied_fraction_without_prorating_it():
    scenario = change(quarter(), lambda p: p["schedules"][0].update(fixed_per_period="2.35"))
    final = project(scenario)[-1]
    bill = final["advisory_fee_assessments"][0]
    assert bill["fixed_charge"] == Decimal("2.35")
    assert bill["assessed"] == final["advisory_fees_paid"] == Decimal("25.35")
    assert final["closing_cash"] == Decimal("974.65")
    assert final["net_wealth"] == Decimal("23974.65")
