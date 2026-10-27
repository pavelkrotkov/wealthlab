"""Unsupported profiles stay visible; a valid baseline is not proof of PR eligibility."""

from decimal import Decimal

import pytest

from wealthlab.tax.pr_examples import synthetic
from wealthlab.tax.pr_facts import PRCase
from wealthlab.tax.pr_guards import guards
from wealthlab.tax.pr_inputs import validate


@pytest.mark.parametrize(
    "field,value,expected",
    [
        ("age_primary", 65, "Senior"),
        ("status", "head", "single/joint"),
        (
            "dependents",
            [
                {
                    "age": 12,
                    "child_credit_eligible": True,
                    "earned_income_credit_eligible": False,
                    "care_credit_eligible": False,
                }
            ],
            "Dependent",
        ),
    ],
)
def test_filing_profiles_are_guarded(field, value, expected):
    data = synthetic().model_dump(mode="json")
    data["baseline"]["filing"][field] = value
    assert expected in " ".join(guards(PRCase.model_validate(data)))


def test_credit_payment_needs_evidence_and_itemized_allocation_is_not_assumed():
    data = synthetic().model_dump(mode="json")
    data["baseline"]["federal_deductions"]["cash_charity"] = "1"
    data["pr_income_tax_paid_for_us_credit"] = "1"
    reasons = " ".join(guards(PRCase.model_validate(data)))
    assert "standard deduction" in reasons
    assert "evidence" in reasons


def test_unknown_wage_reporting_and_citizenship_do_not_qualify():
    data = synthetic().model_dump(mode="json")
    data["pr_wages_reported_on_form_499r2"] = "unset"
    data["primary"]["us_citizen"] = "unset"
    reasons = " ".join(guards(PRCase.model_validate(data)))
    assert "citizenship" in reasons
    assert "reporting" in reasons


def test_calendar_and_spouse_ownership_are_validated():
    case = synthetic()
    person = case.primary.model_copy(update={"presence_days": 366})
    with pytest.raises(ValueError, match="year length"):
        validate(case.model_copy(update={"primary": person}))
    row = case.income[0].model_copy(update={"owner": "spouse"})
    baseline = case.baseline.model_copy(
        update={
            "federal_income": case.baseline.federal_income.model_copy(
                update={"wages_primary": Decimal(0), "wages_spouse": Decimal(100000)}
            )
        }
    )
    with pytest.raises(ValueError, match="Spouse"):
        validate(case.model_copy(update={"income": [row], "baseline": baseline}))
