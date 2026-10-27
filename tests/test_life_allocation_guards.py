"""Removing protection cannot remove its need, existing policy capital or cash cost."""

import pytest

from wealthlab.products.life_allocation_example import synthetic
from wealthlab.products.life_comparison import compare
from wealthlab.products.life_comparison_inputs import LifeComparison


@pytest.mark.parametrize(
    ("target", "field", "value", "message"),
    [
        ("need", "person_a", "0", "insurance needs"),
        ("cash", "balance", "11000", "capital"),
        ("contract", "opening_federal_basis", "1000", "opening policy history"),
        ("contract", "ordinary_personal_contract_confirmed", False, "eligibility"),
        ("holding", "failure_exits", {}, "failure exit"),
    ],
)
def test_unmatched_or_unsupported_new_issue_assumptions_cannot_produce_a_comparison(
    target, field, value, message
):
    data = synthetic().model_dump(mode="json")
    new = data["alternatives"]["new_issue"]
    holding = new["life_plan"]["holdings"][0]
    targets = dict(
        need=new["life_plan"]["insurance_need_by_owner"],
        cash=new["accounts"][0],
        contract=holding["contract"],
        holding=holding,
    )
    targets[target][field] = value
    with pytest.raises(ValueError, match=message):
        compare(LifeComparison.model_validate(data))


def test_uninsured_reference_cannot_hide_a_policy_without_an_actual_opening_exit():
    data = synthetic().model_dump(mode="json")
    data["liquid_reference"] = "new_issue"
    with pytest.raises(ValueError, match="actual opening exit"):
        compare(LifeComparison.model_validate(data))
