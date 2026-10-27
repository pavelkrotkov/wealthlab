"""No date, region or completeness selection silently qualifies a Spanish profile."""

import pytest

from wealthlab.tax.spain import evaluate
from wealthlab.tax.spain_example import synthetic
from wealthlab.tax.spain_inputs import SpainCase


@pytest.mark.parametrize(
    "field,value",
    [
        ("region", None),
        ("region", "navarra"),
        ("residence", "nonresident"),
        ("residence", "special_regime"),
        ("filing", "joint"),
        ("worldwide_inputs_complete_confirmed", False),
        ("recognition_prelimited_confirmed", False),
    ],
)
def test_required_residence_regional_and_completeness_facts_block_instead_of_falling_back(
    field, value
):
    data = synthetic().model_dump(mode="json")
    data[field] = value
    result = evaluate(SpainCase.model_validate(data))
    assert result["income"]["status"] == "blocked"
    assert result["wealth"]["status"] == "blocked"
