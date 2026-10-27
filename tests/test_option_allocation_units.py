"""Integer units change quantities and per-unit money; supplied prices and rates remain fixed."""

import pytest

from wealthlab.products.option_allocation import scale_new_plan
from wealthlab.products.option_engine import run
from wealthlab.products.option_purchase_example import unit_plan


def test_double_unit_execution_capitalizes_current_basis_and_realizes_gross_cash():
    two = scale_new_plan(unit_plan(), 2, per_unit_fees_confirmed=True)
    result = run(two.case)
    assert two.case.marks == unit_plan().case.marks
    assert result["rows"][0]["federal_basis"] == 20004
    assert result["ending"]["cash"] == 26992
    assert result["economic_gain"] == 2992
    assert result["exit_state"]["modeled_cash_exit_complete"]


def test_fee_scaling_is_an_explicit_supplied_assumption():
    with pytest.raises(ValueError, match="absolute stock/contract fee"):
        scale_new_plan(unit_plan(), 2, per_unit_fees_confirmed=False)
