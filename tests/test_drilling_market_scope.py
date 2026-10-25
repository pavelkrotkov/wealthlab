"""Only actual plans and supported physical-price observations enter native cash execution."""

from dataclasses import replace

import pytest
from drilling_market_cases import edited, price_case

from wealthlab.markets.drilling_compile import validate
from wealthlab.markets.household_run import run
from wealthlab.markets.paths import generate
from wealthlab.products.drilling_market import compare


def test_binding_without_an_actual_drilling_plan_cannot_be_used():
    case = price_case()
    missing = case.household.model_copy(update={"drilling_plan": None})
    with pytest.raises(ValueError, match="actual drilling plan"):
        validate(missing, generate(case.market), case.binding)
    with pytest.raises(ValueError, match="complete drilling household"):
        compare(case.model_copy(update={"household": missing}))


def test_total_return_marks_cannot_silently_replace_actual_price_only_receipts():
    case = edited(lambda data: data["market"].update(return_convention="total_return_reinvested"))
    with pytest.raises(ValueError, match="separate price-plus-cash"):
        run(case.household, generate(case.market), case.binding)


def test_direct_batch_with_impossible_negative_price_drop_fails_before_any_wallet_run():
    case = price_case()
    batch = generate(case.market)
    marks = batch.mark_returns.copy()
    marks[0, 0, 0] = -1.01
    invalid = replace(batch, mark_returns=marks)
    with pytest.raises(ValueError, match="cannot exceed one hundred percent"):
        run(case.household, invalid, case.binding)


def test_out_of_range_opening_reference_quote_is_a_clear_unsupported_input():
    case = edited(
        lambda data: data["household"]["drilling_plan"].update(opening_reference_price="1e30")
    )
    with pytest.raises(ValueError, match="supported Decimal quote range"):
        compare(case)
