"""January 1 birthdays have different federal and NJ age-65 instructions."""

from decimal import Decimal as D

from wealthlab.household.scenario import Scenario
from wealthlab.tax.annual import evaluate
from wealthlab.tax.facts import FederalIncome
from wealthlab.tax.nj_facts import NJIncome
from wealthlab.tax.projection_example import template


def test_january_first_65th_birthday_uses_separate_tax_ages(payload):
    payload.update(start="2025-01-01", end="2026-01-01")
    payload["members"] = [payload["members"][0]]
    payload["members"][0]["birth_date"] = "1961-01-01"
    case = template(Scenario.model_validate(payload)).cases[0]
    result = evaluate(
        case.model_copy(
            update={
                "federal_income": FederalIncome(wages_primary=D(120000)),
                "nj_income": NJIncome(wages=D(120000)),
            }
        )
    )
    assert case.filing.age_primary == 65
    assert case.nj_filing is not None
    assert case.nj_filing.age_primary == 64
    assert result["federal"]["standard_deduction"] == 17750
    assert result["new_jersey"]["taxable_income"] == 119000
