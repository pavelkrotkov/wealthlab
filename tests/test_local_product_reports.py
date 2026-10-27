"""Actual complex product audits remain structured through shared report import/re-execution."""

import json

import pytest
from drilling_cases import short as drilling
from qoz_transition_cases import transition as qoz_revision

from wealthlab.household.projection import project
from wealthlab.household.report import encode, payload
from wealthlab.household.storage import loads


@pytest.mark.parametrize(
    ("build", "audit"),
    [
        (drilling, "drilling_audit"),
        (qoz_revision, "qoz_audit"),
    ],
)
def test_actual_audits_stay_structured_and_reproduce_after_report_import(build, audit):
    scenario = build()
    rows = project(scenario)
    text = encode(payload(scenario, rows))
    exported = json.loads(text)
    assert isinstance(exported["months"][-1][audit], (list, dict))
    assert project(loads(text)) == rows
