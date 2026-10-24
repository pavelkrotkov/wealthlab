"""Payment dates remain distinct from accrual months when health costs enter arrears.

The January receipt first pays the oldest July bill, rather than jumping to
current premiums. A receipt a day late cannot satisfy first-of-month liquidity.
"""

from datetime import date
from decimal import Decimal

from tests.test_medicare_cash import calculate, payload
from wealthlab.retirement.medicare import run
from wealthlab.retirement.medicare_example import synthetic


def test_payments_preserve_actual_date_and_fifo_order_for_old_costs():
    result = run(synthetic())
    january_payments = [p for p in result["payments"] if p["date"] == date(2027, 1, 1)]
    assert january_payments[0]["due"] == "spouse_cover:202607"
    assert january_payments[0]["amount"] == Decimal("466.40")
    assert january_payments[0]["member"] == "spouse"
    assert sum(p["amount"] for p in result["payments"] if p["date"].year == 2027) == 17929


def test_same_day_receipt_precedes_current_bills_but_later_receipt_does_not():
    data = payload()
    data["opening_cash"] = 0
    data["receipts"][0].update(date="2026-01-01", amount=1000)
    first = calculate(data)["monthly"][0]
    assert first["unfunded_at_due"] == 0
    data["receipts"][0]["date"] = "2026-01-02"
    first = calculate(data)["monthly"][0]
    assert first["unfunded_at_due"] == Decimal("683.30")
    assert first["unfunded"] == 0
