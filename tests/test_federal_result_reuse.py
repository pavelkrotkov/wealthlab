"""Repeated exact facts reuse immutable raw results, never another household's live arrays.

Fresh-package reference tests continue to own numerical tax correctness. These
counterexamples protect cached result ownership and every independent key axis,
including foreign credits, the requested output set and policy-income NIIT.
"""

import pytest
from test_federal_engine import case

from wealthlab.tax.federal import OUTPUTS
from wealthlab.tax.federal_engine import cached_values, values


@pytest.fixture(autouse=True)
def clear():
    cached_values.cache_clear()
    yield
    cached_values.cache_clear()


def test_repeated_full_input_avoids_recalculation_and_returns_independently_owned_results():
    data = case(2, 500000)
    first = values(data, 2025, OUTPUTS)
    expected = dict(first)
    first["iitax"] = -999999
    reordered = dict(reversed(list(data.items())))
    assert values(reordered, 2025, OUTPUTS) == expected
    assert cached_values.cache_info().misses == 1
    assert cached_values.cache_info().hits == 1
    assert cached_values.cache_info().maxsize == 4096


def test_changed_income_and_year_cannot_reuse_a_previously_valid_household_result():
    data = case(2, 500000)
    original = values(data, 2025, OUTPUTS)
    data.update(e00200=150000, e00200p=150000)
    lower = values(data, 2025, OUTPUTS)
    later = values(data, 2026, OUTPUTS)
    assert lower["c09200"] < original["c09200"]
    assert later != lower
    assert cached_values.cache_info().misses == 3


def test_requested_outputs_and_insurance_adjustment_are_distinct_inputs():
    data = case(2, 500000)
    data.update(e01500=100000, e01700=100000)
    ordinary = values(data, 2025, OUTPUTS)
    policy = values(data, 2025, OUTPUTS, insurance_niit=100000)
    selected = values(data, 2025, ("c09200",), insurance_niit=100000)
    assert policy["niit"] - ordinary["niit"] == 3800
    assert selected == {"c09200": policy["c09200"]}
    assert cached_values.cache_info().misses == 3


def test_foreign_credit_carrier_changes_cannot_hit_the_uncredited_result():
    data = case(2, 500000)
    original = values(data, 2025, ("c09200", "c07300", "taxbc"))
    credited = values(dict(data, e07300=100), 2025, ("c09200", "c07300", "taxbc"))
    assert original["c09200"] - credited["c09200"] == 100
    assert credited["c07300"] == 100
    assert cached_values.cache_info().misses == 2
