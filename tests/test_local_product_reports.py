"""Actual complex product audits remain structured through shared report import/re-execution."""

import json
from decimal import Decimal

import pytest

from wealthlab.household.projection import project
from wealthlab.household.report import encode, payload
from wealthlab.household.storage import loads
from wealthlab.portfolio.saving_example import synthetic as saving
from wealthlab.products.household_example import synthetic as sleeve
from wealthlab.products.life_household_example import synthetic as life
from wealthlab.products.option_household_example import synthetic as options
from wealthlab.retirement.social_work_household_example import synthetic as social_work


@pytest.mark.parametrize(
    ("build", "audit"),
    [
        (saving, "saving_audit"),
        (sleeve, "sleeve_audit"),
        (life, "life_policy_audit"),
        (options, "option_audit"),
        (social_work, "social_security_work_audit"),
    ],
)
def test_actual_audits_stay_structured_and_reproduce_after_report_import(build, audit):
    scenario = build()
    rows = project(scenario)
    text = encode(payload(scenario, rows))
    exported = json.loads(text)
    assert isinstance(exported["months"][-1][audit], (list, dict))
    assert project(loads(text)) == rows


@pytest.mark.parametrize("value", [object(), Decimal("NaN"), float("nan")])
def test_unknown_structures_or_nonfinite_values_cannot_be_flattened_into_a_report(value):
    with pytest.raises(ValueError):
        encode(dict(audit=value))
