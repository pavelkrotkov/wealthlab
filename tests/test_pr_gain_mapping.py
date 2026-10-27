"""Every supplied gain contract must be consumed by exactly its own LTC receipt."""

import pytest

from wealthlab.tax.pr_incentive_examples import legacy_dividends, new_gain
from wealthlab.tax.pr_inputs import income
from wealthlab.tax.pr_tax_slices import prepare


@pytest.mark.parametrize("kind", ["wages", "interest", "dividends", "ordinary"])
def test_gain_cannot_be_silently_dropped_when_mapped_to_another_income_kind(kind):
    comparison = legacy_dividends()
    row = comparison.annual.income[0].model_copy(update={"kind": kind, "qualified_dividends": 0})
    baseline = comparison.annual.baseline.model_copy(update={"federal_income": income([row])})
    annual = comparison.annual.model_copy(update={"income": [row], "baseline": baseline})
    comparison = comparison.model_copy(update={"annual": annual, "gains": new_gain().gains})
    with pytest.raises(ValueError, match="long_term"):
        prepare(comparison)


def test_gain_index_must_reference_an_actual_receipt():
    comparison = new_gain()
    gain = comparison.gains[0].model_copy(update={"income_index": 99})
    with pytest.raises(ValueError, match="absent"):
        prepare(comparison.model_copy(update={"gains": [gain]}))
