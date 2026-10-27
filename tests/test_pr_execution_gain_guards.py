"""A native-looking gain contract cannot invent disposed shares, basis, costs or tax eligibility."""

import pytest
from pr_execution_gain_mutations import fields, mutate

from wealthlab.household.scenario import Scenario
from wealthlab.tax.jurisdiction_execution import evaluate
from wealthlab.tax.pr_execution_gain_example import synthetic_gain


@pytest.mark.parametrize(
    "change",
    [
        "missing_book",
        "unknown_trade",
        "partial_sale",
        "basis",
        "acquired",
        "cost",
        "expense",
        "owner",
    ],
)
def test_invalid_native_sale_or_incomplete_cost_cannot_produce_a_country_candidate(change):
    data = synthetic_gain().model_dump(mode="json")
    profile, source = fields(data)
    mutate(data, profile, source, change)
    with pytest.raises(ValueError):
        evaluate(Scenario.model_validate(data))


def test_positive_mixed_credit_with_different_bases_remains_guarded():
    data = synthetic_gain().model_dump(mode="json")
    profile, _ = fields(data)
    profile["local_us_credit_treatment"] = "allowed"
    with pytest.raises(ValueError, match="different recognized bases"):
        evaluate(Scenario.model_validate(data))


def test_unvalidated_positive_us_preferential_ftc_is_not_created_by_the_new_source_kind():
    data = synthetic_gain().model_dump(mode="json")
    data["foreign_tax_plan"]["credit_profiles"][0]["eligibility"] = "allowed"
    final = evaluate(Scenario.model_validate(data))["rows"][-1]
    assert final["annual_tax"]["federal"]["foreign_tax_credit"] == 0
    assert any("Preferential" in reason for reason in final["foreign_tax_unresolved"])
    assert final["funding_failure"]


def test_blank_profile_evidence_cannot_complete_a_native_source_gain():
    data = synthetic_gain().model_dump(mode="json")
    data["tax_plan"]["cases"][0]["pr_federal"]["gain_profile"]["source"] = "  "
    with pytest.raises(ValueError, match="independent source evidence"):
        evaluate(Scenario.model_validate(data))
