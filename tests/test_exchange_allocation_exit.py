"""Completed exits sell actual source/basket shares before reporting household cash."""

import pytest
from exchange_allocation_cases import allocated

from wealthlab.household.projection import project
from wealthlab.products.exchange_fund_compare import compare


@pytest.mark.parametrize("quantity", [0, 400, 1000])
def test_all_native_allocation_choices_close_only_after_full_actual_sales(quantity):
    result = compare(allocated(quantity))
    for rows in result["rows"].values():
        final = rows[-1]
        assert final["exchange_source_sale_cash"] == (1000 - quantity) * 100
        assert final["exchange_positions_closed"] is True
        assert final["exchange_fund_audit"]["remaining_lots"] == []
        assert final["annual_tax"]["federal"]["agi"] == 80000
        assert final["annual_tax"]["new_jersey"]["gross_income"] == 70000
        assert final["net_wealth"] == 130000 - final["annual_tax"]["total_liability"]


@pytest.mark.parametrize("quantity", [0, 400])
def test_basket_exit_does_not_close_or_sell_unscheduled_retained_source(quantity):
    final = project(allocated(quantity, source_sale=False))[-1]
    assert final["exchange_retained_source_quantity"] == 1000 - quantity
    assert final["account_balances"]["exchange"] == (1000 - quantity) * 100
    assert final["exchange_positions_closed"] is False
    assert final["exchange_fund_audit"]["exit_status"]["modeled_exit_complete"] is False
