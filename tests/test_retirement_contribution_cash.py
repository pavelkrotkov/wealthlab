"""Dated receipts and multiple account orders must conserve capital."""

from decimal import Decimal

from test_retirement_contributions import calculate, case_for


def test_cash_receipt_after_order_cannot_fund_the_past():
    data = case_for("traditional_ira", amount="7500.00")
    data["opening_cash"] = "1000.00"
    data["receipts"] = [
        dict(id="receipt", provenance="assumption", date="2026-02-01", amount="6500.00")
    ]
    result = calculate(data)
    assert result["orders"][0]["funded"] == 1000
    assert result["orders"][0]["unfunded"] == 6500
    assert result["cash"] == 6500
    data["receipts"][0]["date"] = "2026-01-15"
    assert calculate(data)["orders"][0]["funded"] == 7500


def test_opening_balances_and_owner_limits_conserve_total_capital():
    data = case_for("pretax_401k", amount="20000.00", workplace_compensation="25000.00")
    data["accounts"][0]["balance"] = "1234.56"
    order = dict(data["orders"][0], id="second", amount="20000.00")
    data["orders"].append(order)
    result = calculate(data)
    assert [row["funded"] for row in result["orders"]] == [20000, 4500]
    assert result["cash"] + sum(result["account_balances"].values()) == Decimal("201234.56")
