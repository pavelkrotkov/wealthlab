"""Candidate compilation cannot bypass offered bounds or confirm an existing sleeve implicitly.

These boundaries apply even to a direct compiler caller rather than only the
search loop. Adding a new explicitly confirmed investment does not establish
that the user agreed to replace the observation history of a current holding.
"""

import pytest
from optimization_allocation_cases import case
from optimization_cases import flat

from wealthlab.optimization.allocation_example import extend
from wealthlab.optimization.compile import compile_candidate
from wealthlab.optimization.inputs import PolicyChoice, PolicySearch
from wealthlab.optimization.product_example import extend as with_products
from wealthlab.optimization.validation import validate


@pytest.mark.parametrize(
    "units,message",
    [
        ({"missing": 1}, "configured sleeve"),
        ({"new_margin": 6}, "within the supplied bounds"),
    ],
)
def test_direct_candidate_still_obeys_opportunity_identity_and_bounds(units, message):
    with pytest.raises(ValueError, match=message):
        compile_candidate(case(), [PolicyChoice(id="direct", sleeve_units=units)])


def test_duplicate_direct_allocation_writes_are_rejected_before_debiting_cash_twice():
    choice = PolicyChoice(id="one", sleeve_units={"new_margin": 1})
    with pytest.raises(ValueError, match="one dimension only"):
        compile_candidate(case(), [choice, choice])


def test_new_purchase_cannot_confirm_replacement_of_existing_sleeve_observations():
    data = extend(with_products(flat())).model_dump(mode="json")
    data["binding"]["replace_sleeve_observations_confirmed"] = False
    with pytest.raises(ValueError, match="original sleeve observations independently"):
        validate(PolicySearch.model_validate(data))
