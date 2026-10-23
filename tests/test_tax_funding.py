"""Withdrawal tax creates a cash need of its own; illiquid assets cannot cover it."""

from decimal import Decimal as D

from wealthlab.tax.funding import solve


def test_withdrawal_funds_its_own_tax_without_borrowing():
    # $80 spending needs $100 liquidation with a 20% realization tax.
    result = solve(D(0), D(80), D(200), lambda amount: amount * D(".2"))
    assert result["withdrawal"] == 100
    assert result["spending_shortfall"] == 0
    assert result["tax_unpaid"] == 0
    assert result["converged"]


def test_insufficient_assets_reports_unpaid_obligations():
    result = solve(D(10), D(100), D(50), lambda amount: D(20) + amount * D(".2"))
    assert result["withdrawal"] == 50
    assert result["tax_paid"] == 30
    assert result["spending_paid"] == 30
    assert result["spending_shortfall"] == 70
    assert result["cash_left"] == 0


def test_refund_is_receivable_until_received():
    result = solve(D(0), D(20), D(0), lambda _: D(-100))
    assert result["refund_receivable"] == 100
    assert result["spending_shortfall"] == 20
    assert result["cash_left"] == 0


def test_tax_cliff_is_funded_and_iteration_cap_is_visible():
    result = solve(D(0), D(80), D(500), lambda amount: D(50) if amount > 50 else D(0))
    assert result["withdrawal"] == 130
    assert result["spending_shortfall"] == 0
    capped = solve(D(0), D(10), D(10000), lambda amount: amount)
    assert not capped["converged"]
    assert capped["spending_shortfall"] == 10
