"""Integer units change quantities and per-unit money; supplied prices and rates remain fixed."""

import pytest

from wealthlab.products.option_allocation import required_capital, scale_new_plan
from wealthlab.products.option_engine import run
from wealthlab.products.option_purchase_example import unit_plan


def test_two_new_units_consume_double_cash_and_execute_double_shares_fees_and_basis():
    original = unit_plan()
    before = original.model_dump_json()
    two = scale_new_plan(original, 2, per_unit_fees_confirmed=True)
    assert original.model_dump_json() == before
    assert required_capital(two) == 24000
    assert not two.case.holdings.lots
    # Quantities and confirmed absolute fees scale together; unit premiums and
    # strikes stay fixed so larger allocations do not acquire cheaper contracts.
    purchase = two.case.opening_stock_purchase
    assert purchase is not None
    assert (purchase.shares, purchase.fee) == (200, 4)
    leg = two.case.legs[0]
    assert (leg.contracts, leg.premium, leg.strike) == (2, 5, 110)
    assert (leg.opening_fee, leg.closing_fee, two.case.stock_sale_fee) == (2, 2, 2)


def test_double_unit_execution_capitalizes_current_basis_and_realizes_gross_cash():
    two = scale_new_plan(unit_plan(), 2, per_unit_fees_confirmed=True)
    result = run(two.case)
    assert two.case.marks == unit_plan().case.marks
    assert result["rows"][0]["federal_basis"] == 20004
    assert result["ending"]["cash"] == 26992
    assert result["economic_gain"] == 2992
    assert result["exit_state"]["modeled_cash_exit_complete"]


@pytest.mark.parametrize("count", [0, -1, 1.5, True, 100001])
def test_no_fractional_boolean_negative_or_unbounded_contract_units(count):
    with pytest.raises(ValueError, match="bounded integers"):
        scale_new_plan(unit_plan(), count, per_unit_fees_confirmed=True)


def test_fee_scaling_is_an_explicit_supplied_assumption():
    with pytest.raises(ValueError, match="absolute stock/contract fee"):
        scale_new_plan(unit_plan(), 2, per_unit_fees_confirmed=False)
