"""Bounds, locks and paired assumptions are checked before any expensive path projection."""

import pytest
from optimization_cases import changed, flat

from wealthlab.optimization.validation import validate


def test_lock_removes_choices_from_grid_without_mutating_declared_options():
    case = changed(flat(), lambda d: d["dimensions"][0].update(locked_choice="early"))
    assert validate(case) == 1
    assert len(case.dimensions[0].choices) == 2


@pytest.mark.parametrize("lock", ["missing", "later_typo"])
def test_unknown_lock_cannot_silently_execute_no_candidates(lock):
    case = changed(flat(), lambda d: d["dimensions"][0].update(locked_choice=lock))
    with pytest.raises(ValueError, match="allowed choice"):
        validate(case)


@pytest.mark.parametrize(
    "field,value,pattern",
    [
        ("seed", 71, "seeds must differ"),
        ("expected_annual_inflation", 0.04, "same market assumptions"),
        ("mode", "deterministic", "Monte Carlo"),
    ],
)
def test_validation_must_be_new_sample_of_same_experiment(field, value, pattern):
    case = changed(flat(), lambda d: d["validation"].update({field: value}))
    with pytest.raises(ValueError, match=pattern):
        validate(case)


@pytest.mark.parametrize(
    "field,value", [("maximum_candidates", 1), ("maximum_projection_months", 1)]
)
def test_explicit_work_bounds_are_enforced(field, value):
    case = changed(flat(), lambda d: d.update({field: value}))
    with pytest.raises(ValueError, match="budget"):
        validate(case)


def test_overlapping_dimensions_cannot_overwrite_a_locked_retirement_choice():
    case = changed(
        flat(), lambda d: d["dimensions"].append(dict(d["dimensions"][0], id="duplicate"))
    )
    with pytest.raises(ValueError, match="same policy"):
        validate(case)


def test_choices_in_one_dimension_must_control_the_same_members():
    case = changed(
        flat(),
        lambda d: d["dimensions"][0]["choices"][1].update(
            retirement_dates={"person_b": "2027-01-01"}
        ),
    )
    with pytest.raises(ValueError, match="same policy fields"):
        validate(case)
