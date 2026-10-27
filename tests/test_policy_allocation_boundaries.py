"""Candidate compilation cannot bypass offered bounds or confirm an existing sleeve implicitly.

These boundaries apply even to a direct compiler caller rather than only the
search loop. Adding a new explicitly confirmed investment does not establish
that the user agreed to replace the observation history of a current holding.
"""

import pytest
from optimization_cases import flat

from wealthlab.optimization.allocation_example import extend
from wealthlab.optimization.inputs import PolicySearch
from wealthlab.optimization.product_example import extend as with_products
from wealthlab.optimization.validation import validate


def test_new_purchase_cannot_confirm_replacement_of_existing_sleeve_observations():
    data = extend(with_products(flat())).model_dump(mode="json")
    data["binding"]["replace_sleeve_observations_confirmed"] = False
    with pytest.raises(ValueError, match="original sleeve observations independently"):
        validate(PolicySearch.model_validate(data))
