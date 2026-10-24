"""Tax-exempt income can change future Medicare premiums without changing federal AGI."""

from datetime import date
from decimal import Decimal

from wealthlab.household.projection import project
from wealthlab.retirement.medicare_household_example import synthetic
from wealthlab.tax.facts import FederalIncome
from wealthlab.tax.nj_facts import NJIncome
from wealthlab.tax.projection_inputs import TaxEvent


def test_completed_income_adds_tax_exempt_interest_to_irmaa_magi():
    case = synthetic()
    event = TaxEvent(
        date=date(2026, 6, 1),
        description="Supplied exempt income",
        cash_received=0,
        federal=FederalIncome(tax_exempt_interest=5000),
        new_jersey=NJIncome(),
    )
    taxes = case.tax_plan.model_copy(update=dict(events=[event]))
    rows = project(case.model_copy(update=dict(tax_plan=taxes)))
    assert rows[11]["annual_tax"]["federal"]["agi"] == 270000
    assert rows[24]["medicare_due"] == Decimal("1366.60")
    record = next(i for i in rows[-1]["medicare_audit"]["income_history"] if i["year"] == 2026)
    assert record["agi"] + record["tax_exempt_interest"] == 275000
