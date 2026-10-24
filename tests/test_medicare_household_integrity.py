"""Exports preserve prior facts; generated future return history remains runtime-only.

The editable starter leaves enrollment and history unconfirmed. Its temporary
record IDs must remain distinct even when household members use the same
valid identifiers that a simple sequential starter would otherwise choose.
"""

import pytest

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.household.storage import loads
from wealthlab.retirement.medicare_household_example import synthetic
from wealthlab.retirement.medicare_household_inputs import MedicarePlan
from wealthlab.retirement.medicare_household_template import template


def test_original_prior_returns_are_immutable_and_round_trip_reproduces():
    case = synthetic()
    original = case.model_dump_json()
    rows = project(case)
    assert case.model_dump_json() == original
    assert len(case.medicare_plan.case.income_history) == 2
    assert project(loads(original)) == rows


def test_prior_record_cannot_alias_generated_household_return_id():
    case = synthetic()
    source = case.medicare_plan.case
    renamed = source.income_history[0].model_copy(update=dict(id="household_return_2026"))
    source = source.model_copy(update=dict(income_history=[renamed, source.income_history[1]]))
    plan = case.medicare_plan.model_copy(update=dict(case=source))
    with pytest.raises(ValueError, match="reserved"):
        project(case.model_copy(update=dict(medicare_plan=plan)))


def test_one_person_starter_is_editable_and_remains_unconfirmed():
    case = synthetic()
    plan = template(case.model_copy(update=dict(members=case.members[:1])))
    assert len(plan["case"]["members"]) == 1
    assert all(i["filing"] == "individual" for i in plan["case"]["income_history"])
    assert not plan["case"]["complete_context"]
    assert not plan["case"]["coverage"][0]["eligibility_confirmed"]
    assert not plan["complete_household_tax_history_confirmed"]


def test_starter_ids_cannot_collide_with_valid_household_member_ids():
    raw = (
        synthetic()
        .model_dump_json()
        .replace('"person_a"', '"coverage_0"')
        .replace('"person_b"', '"_coverage_0"')
    )
    case = Scenario.model_validate_json(raw)
    payload = template(case)
    payload["case"]["complete_context"] = True
    for coverage in payload["case"]["coverage"]:
        coverage["eligibility_confirmed"] = True
    starter = MedicarePlan.model_validate(payload).case
    records = [*starter.members, *starter.coverage, *starter.income_history]
    assert len({r.id for r in records}) == len(records)
