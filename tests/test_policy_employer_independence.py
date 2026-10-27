"""A fixed former-employer contract needs explicit source coverage, never inferred owner linkage.

Existing source events remain shared across working/retired choices only when
all original tranches and the entire candidate employment envelope are covered.
"""

import pytest
from optimization_contract_cases import case
from optimization_employment_cases import flat

from wealthlab.optimization.compile import compile_candidate
from wealthlab.optimization.inputs import PolicySearch
from wealthlab.optimization.validation import validate


def test_former_employer_starter_retains_explicit_independence_and_all_native_events():
    profile = case()
    assert profile.employer_independence is not None
    assert validate(profile) == 1
    household, _ = compile_candidate(profile, [profile.dimensions[0].choices[0]])
    assert household.compensation_plan == profile.household.compensation_plan


@pytest.mark.parametrize(
    "edit,message",
    [
        (lambda p: p.update(employer_independence=None), "Supply employer independence"),
        (
            lambda p: p["employer_independence"].update(tranche_ids=["wrong"]),
            "every original tranche",
        ),
        (
            lambda p: p["employer_independence"].update(tranche_ids=["award", "award"]),
            "every original tranche",
        ),
        (
            lambda p: p["employer_independence"].update(
                independent_of_all_candidate_employment_and_retirement_confirmed=False
            ),
            "independent of every",
        ),
        (
            lambda p: p["employer_independence"].update(provenance="unresolved"),
            "Resolve the source",
        ),
    ],
)
def test_independence_cannot_be_missing_partial_or_unconfirmed(edit, message):
    data = case().model_dump(mode="json")
    edit(data)
    with pytest.raises(ValueError, match=message):
        validate(PolicySearch.model_validate(data))


def test_independence_cannot_compete_with_source_matched_current_employer_offers():
    data = flat().model_dump(mode="json")
    data["employer_independence"] = case().employer_independence.model_dump(mode="json")
    with pytest.raises(ValueError, match="either fixed employer independence"):
        validate(PolicySearch.model_validate(data))


def test_applicability_cannot_reference_an_absent_employer_book():
    data = case().model_dump(mode="json")
    data["household"]["compensation_plan"] = None
    with pytest.raises(ValueError, match="original compensation plan"):
        validate(PolicySearch.model_validate(data))
