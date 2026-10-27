"""Derived stock source rules require the supported residency at disposition."""

import pytest

from wealthlab.tax.pr_incentive_examples import new_gain
from wealthlab.tax.pr_tax_slices import prepare


@pytest.mark.parametrize("status", ["no", "move_out"])
def test_non_bfr_and_departure_stock_sales_do_not_inherit_pr_source(status):
    comparison = new_gain()
    person = comparison.annual.primary.model_copy(update={"federal_bfr": status})
    annual = comparison.annual.model_copy(update={"primary": person})
    with pytest.raises(ValueError, match="full-year BFR"):
        prepare(comparison.model_copy(update={"annual": annual}))


def test_stock_sale_cannot_follow_the_explicit_local_residence_end():
    comparison = new_gain()
    person = comparison.annual.primary.model_copy(update={"local_end": None})
    annual = comparison.annual.model_copy(update={"primary": person})
    with pytest.raises(ValueError, match="local PR residence"):
        prepare(comparison.model_copy(update={"annual": annual}))
