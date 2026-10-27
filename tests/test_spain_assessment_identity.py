"""Stable annual and payment identities prevent repeated credit recognition across people/years."""

import pytest
from spain_cases import payment

from wealthlab.tax.spain_assessment_example import synthetic_plan
from wealthlab.tax.spain_assessment_inputs import SpainAssessmentPlan


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        ("duplicate_annual", "person and liability year"),
        ("duplicate_plan_id", "record IDs"),
        ("unknown_assessment", "identify an annual"),
        ("old_due_date", "predate its liability year"),
        ("future_observation", "as-of date"),
        ("incomplete_year", "completed calendar year"),
        ("provenance", "synthetic provenance"),
    ],
)
def test_invalid_cross_case_identity_or_chronology_is_rejected(mutation, message):
    data = synthetic_plan().model_dump(mode="json")
    if mutation == "duplicate_annual":
        data["annuals"][1]["case"] = data["annuals"][0]["case"]
    elif mutation == "duplicate_plan_id":
        data["obligations"][0]["id"] = data["annuals"][0]["id"]
    elif mutation == "unknown_assessment":
        data["obligations"][0]["assessment_id"] = "absent"
    elif mutation == "old_due_date":
        data["obligations"][0]["due_date"] = "2024-12-31"
    elif mutation == "future_observation":
        data["annuals"][0]["case"]["as_of"] = "2028-01-01"
    elif mutation == "incomplete_year":
        data["annuals"][0]["case"]["as_of"] = "2025-06-30"
    else:
        data["annuals"][0]["case"]["synthetic"] = False
    with pytest.raises(ValueError, match=message):
        SpainAssessmentPlan.model_validate(data)


def test_same_payment_identity_cannot_be_used_by_two_individual_assessments():
    data = synthetic_plan().model_dump(mode="json")
    data["annuals"][0]["case"]["payments"] = [payment("100")]
    other = payment("100")
    other["owner_id"] = "synthetic_other"
    data["annuals"][2]["case"]["payments"] = [other]
    with pytest.raises(ValueError, match="payment ID"):
        SpainAssessmentPlan.model_validate(data)
