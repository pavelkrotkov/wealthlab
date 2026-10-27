"""Complete supplied profiles retain native tax-owner and wage-state validation.

Inactive profiles are preflighted through the native preparation functions.
No search choice may fix an invalid source by merely leaving it unselected.
"""

from copy import deepcopy

import pytest
from optimization_employment_cases import changed, flat

from wealthlab.optimization.inputs import PolicySearch
from wealthlab.optimization.validation import validate


def test_inactive_profile_still_checks_native_income_owner():
    def edit(data):
        allocation = data["employment_offers"][0]["compensation_plan"]["events"][2]
        allocation["federal"] = dict(wages_spouse="20000")

    with pytest.raises(ValueError, match="tranche owner"):
        validate(changed(edit))


def test_duplicate_offer_ids_and_unshared_compiled_tax_allocations_are_rejected():
    data = flat().model_dump(mode="json")
    data["employment_offers"].append(deepcopy(data["employment_offers"][0]))
    with pytest.raises(ValueError, match="offer IDs must be unique"):
        validate(PolicySearch.model_validate(data))
    data = flat().model_dump(mode="json")
    plan = data["employment_offers"][0]["compensation_plan"]
    plan["compiled_allocations"] = [deepcopy(plan["events"][2])]
    with pytest.raises(ValueError, match="compiled allocations fixed"):
        validate(PolicySearch.model_validate(data))


def test_one_retirement_date_map_cannot_offer_competing_contract_assumptions():
    data = flat().model_dump(mode="json")
    extra = deepcopy(data["employment_offers"][0])
    extra["id"] = "different_assumptions"
    data["employment_offers"].append(extra)
    with pytest.raises(ValueError, match="one unambiguous employer profile"):
        validate(PolicySearch.model_validate(data))
