"""Complete supplied profiles retain native tax-owner and wage-state validation.

Inactive profiles are preflighted through the native preparation functions.
No search choice may fix an invalid source by merely leaving it unselected.
"""

from copy import deepcopy

import pytest
from optimization_employment_cases import changed, flat

from wealthlab.optimization.compile import compile_candidate
from wealthlab.optimization.inputs import PolicySearch
from wealthlab.optimization.validation import validate


def test_inactive_profile_still_checks_native_income_owner():
    def edit(data):
        allocation = data["employment_offers"][0]["compensation_plan"]["events"][2]
        allocation["federal"] = dict(wages_spouse="20000")

    with pytest.raises(ValueError, match="tranche owner"):
        validate(changed(edit))


def test_inactive_work_state_transition_still_uses_native_validation():
    def edit(data):
        data["employment_offers"][0]["employment_plan"]["paths"][0]["changes"][0].update(
            kind="return_to_work", multiplier="1"
        )

    with pytest.raises(ValueError, match="Inconsistent return_to_work"):
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


def test_baseline_replay_preserves_original_native_profiles():
    case = flat()
    household, binding = compile_candidate(case, [])
    assert household.compensation_plan == case.household.compensation_plan
    assert household.employment_plan == case.household.employment_plan
    assert binding == case.binding


def test_two_complete_profile_selections_cannot_override_one_another():
    case = flat()
    with pytest.raises(ValueError, match="Only one dimension"):
        compile_candidate(case, case.dimensions[0].choices)


def test_changed_dates_cannot_bypass_profile_selection_in_direct_compilation():
    from datetime import date

    from wealthlab.optimization.inputs import PolicyChoice

    case = flat()
    choice = PolicyChoice(id="dates_only", retirement_dates={"person_a": date(2026, 1, 1)})
    with pytest.raises(ValueError, match="Changed retirement dates"):
        compile_candidate(case, [choice])


def test_one_retirement_date_map_cannot_offer_competing_contract_assumptions():
    data = flat().model_dump(mode="json")
    extra = deepcopy(data["employment_offers"][0])
    extra["id"] = "different_assumptions"
    data["employment_offers"].append(extra)
    with pytest.raises(ValueError, match="one unambiguous employer profile"):
        validate(PolicySearch.model_validate(data))
