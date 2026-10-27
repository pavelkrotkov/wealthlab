"""Explicit same-day ordering changes economic exposure; allocations compile exactly once."""

from datetime import date

import pytest

from wealthlab.employment.compensation_example import synthetic
from wealthlab.employment.compensation_projection import prepare
from wealthlab.household.projection import project


def test_sequence_controls_whether_a_grant_participates_in_the_same_day_return():
    case = synthetic()
    moved = [
        e.model_copy(update=dict(date=date(2026, 3, 1), sequence=1)) if e.kind == "grant" else e
        for e in case.compensation_plan.events
    ]
    plan = case.compensation_plan.model_copy(update=dict(events=moved))
    changed = case.model_copy(update=dict(compensation_plan=plan))
    rows = project(changed)
    assert rows[2]["employer_unvested_contingent"] == 98000
    reversed_plan = plan.model_copy(update=dict(events=list(reversed(moved))))
    assert project(case.model_copy(update=dict(compensation_plan=reversed_plan))) == rows


def test_duplicate_same_day_sequence_is_rejected():
    case = synthetic()
    events = list(case.compensation_plan.events)
    events[0] = events[0].model_copy(update=dict(date=events[1].date))
    plan = case.compensation_plan.model_copy(update=dict(events=events))
    with pytest.raises(ValueError, match="distinct explicit sequence"):
        prepare(case.model_copy(update=dict(compensation_plan=plan)))
