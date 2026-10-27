"""Existing native ownership and wash groups cannot change when search begins.

The native source fixture is jointly owned. Its household account must preserve
that fact; a primary/spouse role names the corresponding real member instead.
"""

import pytest
from optimization_cases import changed
from optimization_contract_cases import case

from wealthlab.optimization.compile import compile_candidate


def test_existing_joint_source_keeps_joint_household_ownership():
    profile = case()
    account = next(a for a in profile.household.accounts if a.id == "options")
    assert account.owner == profile.household.option_plan.case.holdings.accounts[0].owner == "joint"
    compiled, _ = compile_candidate(profile, [])
    assert next(a for a in compiled.accounts if a.id == "options").owner == "joint"


@pytest.mark.parametrize("role,owner", [("primary", "person_a"), ("spouse", "person_b")])
def test_native_roles_map_to_actual_members_without_changing_other_facts(role, owner):
    def edit(data):
        data["household"]["option_plan"]["case"]["holdings"]["accounts"][0]["owner"] = role
        next(a for a in data["household"]["accounts"] if a["id"] == "options")["owner"] = owner

    profile = changed(case(), edit)
    household, _ = compile_candidate(profile, [])
    assert next(a for a in household.accounts if a.id == "options").owner == owner


def test_search_cannot_retitle_an_existing_joint_option_book_to_one_member():
    def edit(data):
        next(a for a in data["household"]["accounts"] if a["id"] == "options")["owner"] = "person_a"

    with pytest.raises(ValueError, match="owner role"):
        compile_candidate(changed(case(), edit), [])


def test_known_identical_option_and_household_securities_require_cross_book_wash_support():
    def edit(data):
        group = data["household"]["lot_plan"]["case"]["securities"][0]["wash_group"]
        data["household"]["option_plan"]["case"]["holdings"]["securities"][0]["wash_group"] = group

    with pytest.raises(ValueError, match="distinct wash groups"):
        compile_candidate(changed(case(), edit), [])
