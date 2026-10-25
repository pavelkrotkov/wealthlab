"""Wash-split source pieces remain source stock and need an actual source order."""

from exchange_allocation_cases import allocated

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario


def loss_case(source_sale):
    data = allocated(400, source_sale=source_sale).model_dump(mode="json")
    plan = data["exchange_fund_plan"]
    plan["mode"] = "direct_sale"
    plan["source_lot"].update(acquired="2025-12-15", federal_basis="150000", nj_basis="120000")
    return Scenario.model_validate(data)


def test_basket_sale_never_sells_retained_stock_with_a_wash_generated_lot_id():
    final = project(loss_case(False))[-1]
    assert final["exchange_sale_cash"] == 40000
    assert final["exchange_retained_source_quantity"] == 600
    assert final["exchange_retained_source_federal_basis"] == 110000
    assert final["exchange_retained_source_nj_basis"] == 72000
    assert final["exchange_positions_closed"] is False


def test_one_real_source_order_consumes_all_wash_split_units_and_independent_basis():
    final = project(loss_case(True))[-1]
    disposals = final["exchange_fund_audit"]["disposals"]
    assert final["exchange_source_quantity_sold"] == 600
    assert final["exchange_source_sale_cash"] == 60000
    assert sum(row["federal_recognized_gain"] for row in disposals) == -50000
    assert sum(row["nj_recognized_gain"] for row in disposals) == -20000
    assert final["exchange_positions_closed"] is True
