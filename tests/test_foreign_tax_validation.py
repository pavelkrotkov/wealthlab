"""Unknown owners, stale FX and duplicate credit/payment facts cannot execute as valid cash.

An assessment is not sufficient proof of a source, person or payment. These
input boundaries reject before wallet funding, while an unresolved credit
keeps the actual foreign tax cost and withholds its favorable US result.
"""

import pytest

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.tax.foreign_tax_example import synthetic


@pytest.mark.parametrize(
    "path,value",
    [
        (("assessments", 0, "owner_id"), "person_b"),
        (("schedules", 0, "assessment_id"), "missing_assessment"),
        (("schedules", 0, "source_income_year"), 2024),
        (("schedules", 0, "source_income_year"), None),
        (("credit_profiles", 0, "people", "person_a"), "spouse"),
    ],
)
def test_unsafe_owner_or_source_identity_rejects_before_projection(path, value):
    data = synthetic().model_dump(mode="json")
    target = data["foreign_tax_plan"]
    for component in path[:-1]:
        target = target[component]
    target[path[-1]] = value
    with pytest.raises(ValueError):
        project(Scenario.model_validate(data))


def test_stale_fx_cannot_silently_value_later_month_claims_at_an_earlier_quote():
    data = synthetic().model_dump(mode="json")
    data["foreign_tax_plan"]["quotes"] = data["foreign_tax_plan"]["quotes"][:1]
    with pytest.raises(ValueError, match="every observed month-end"):
        project(Scenario.model_validate(data))


def test_foreign_assessment_cannot_be_revised_before_its_information_date():
    data = synthetic().model_dump(mode="json")
    data["foreign_tax_plan"]["revisions"] = [
        dict(
            assessment_id="es_income_2025",
            observed="2025-09-01",
            amount_native="0",
            source="Synthetic invalid pre-observation revision",
        )
    ]
    with pytest.raises(ValueError, match="cannot precede"):
        project(Scenario.model_validate(data))


def test_another_positive_foreign_credit_input_cannot_duplicate_the_book_claim():
    data = synthetic().model_dump(mode="json")
    data["tax_plan"]["cases"][0]["foreign_credits"] = dict(
        regular="1000",
        eligibility="allowed",
        source="Synthetic duplicate external claim",
    )
    with pytest.raises(ValueError, match="own its credit"):
        project(Scenario.model_validate(data))


def test_foreign_plan_cannot_silently_disappear_when_domestic_ledger_is_disabled():
    data = synthetic().model_dump(mode="json")
    data["tax_plan"] = None
    with pytest.raises(ValueError, match="requires the household annual tax plan"):
        Scenario.model_validate(data)


def test_an_unscheduled_remaining_assessment_is_not_a_supported_funding_success():
    data = synthetic().model_dump(mode="json")
    data["foreign_tax_plan"]["schedules"] = []
    row = project(Scenario.model_validate(data))[0]
    assert row["foreign_tax_position"] == 11000
    assert row["foreign_tax_paid"] == 0
    assert row["foreign_tax_unresolved"]
    assert row["funding_failure"]


def test_post_credit_settlement_deduction_changes_require_their_own_supported_profile():
    data = synthetic().model_dump(mode="json")
    data["tax_plan"]["state_deduction_mode"] = "actual_payments"
    with pytest.raises(ValueError, match="requires entered state deductions"):
        project(Scenario.model_validate(data))
