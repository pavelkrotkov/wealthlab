"""Constraints preserve marked holdings and expose remaining target gaps.

A sale lock differs from a target lock: the latter can leave spendable sale cash
without completing the allocation. Neither lock destroys the marked asset.
The sale cap measures one-way gross disposals, while the drift band determines
whether a decision starts at all. These are independent economic constraints.
"""

from datetime import date
from decimal import Decimal

import pytest
from rebalance_cases import book_case

from wealthlab.portfolio.rebalance import decide


@pytest.mark.parametrize(
    "changes,status",
    [
        (dict(max_sale_fraction="0"), "constrained"),
        (dict(drift_band=".5"), "within drift band"),
        (dict(commission_per_trade="500"), "constrained"),
    ],
)
def test_unexecutable_decisions_do_not_create_cash_or_trades(changes, status):
    book, policy, prices = book_case(**changes)
    result = decide(book, policy, prices, set())
    assert result["status"] == status
    assert not book.history
    assert result["residual_cash"] == 0


def test_sale_cap_leaves_reported_drift_without_new_cash():
    book, policy, prices = book_case(max_sale_fraction=".1")
    result = decide(book, policy, prices, set())
    rows = {row["security_id"]: row for row in result["securities"]}
    assert result["gross_sales"] == result["gross_purchases"] == 100
    assert rows["stock"]["weight_after"] == Decimal(".9")
    assert rows["bond"]["remaining_target_value"] == 400


def test_source_lock_keeps_stock_and_blocks_purchases():
    book, policy, prices = book_case()
    result = decide(book, policy, prices, {"stock"})
    assert result["status"] == "constrained"
    assert not book.history
    assert next(r for r in result["securities"] if r["security_id"] == "stock")["market_locked"]


def test_target_lock_leaves_real_sale_proceeds_for_household_sweep():
    book, policy, prices = book_case()
    result = decide(book, policy, prices, {"bond"})
    assert result["gross_sales"] == 500
    assert result["gross_purchases"] == 0
    assert result["residual_cash"] == 500


def test_dated_lot_lock_and_no_positions_cannot_manufacture_sales():
    book, policy, prices = book_case()
    book.lots = {
        key: lot.model_copy(update=dict(liquid_after=date(2028, 1, 1)))
        for key, lot in book.lots.items()
    }
    assert decide(book, policy, prices, set())["status"] == "constrained"
    book.lots = {}
    assert decide(book, policy, prices, set())["status"] == "no marked securities"
