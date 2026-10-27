"""Existing cash and quantity precision cannot create additional purchase funding."""

from decimal import Decimal

from rebalance_cases import book_case

from wealthlab.portfolio.rebalance import decide


def test_initial_brokerage_cash_cannot_finance_rebalance_top_up():
    book, policy, prices = book_case(commission_per_trade="1")
    book.cash[policy.account_id] = Decimal(777)
    result = decide(book, policy, prices, set())
    assert book.cash[policy.account_id] == 777
    assert result["gross_purchases"] == 498


def test_six_decimal_share_rounding_keeps_cash_nonnegative():
    book, policy, prices = book_case(commission_per_trade=".01")
    prices["bond"] = Decimal("137.12345678")
    result = decide(book, policy, prices, set())
    assert Decimal(0) <= result["residual_cash"] < Decimal(".01")
    assert result["gross_purchases"] <= Decimal("499.98")


def test_next_decision_uses_observed_shock_prices_and_remaining_shares():
    from datetime import date

    book, policy, prices = book_case()
    decide(book, policy, prices, set())
    prices["stock"] = Decimal(200)
    second = policy.model_copy(update=dict(id="second", date=date(2026, 2, 28)))
    result = decide(book, second, prices, set())
    assert result["gross_sales"] == result["gross_purchases"] == 250
    assert book.history[2].quantity == Decimal("1.25")
    assert all(row["weight_after"] == Decimal(".5") for row in result["securities"])
