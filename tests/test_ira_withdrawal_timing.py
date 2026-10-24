"""Later market events cannot change previously funded withdrawals."""

from decimal import Decimal

from test_ira_withdrawals import calculate, payload


def test_later_returns_reconcile_tax_without_changing_earlier_cash_decisions():
    data = payload()
    before = calculate(data)
    data["returns"] = [
        dict(id="return", provenance="assumption", date="2026-12-31", account_id="ira", rate="1.0")
    ]
    after = calculate(data)
    assert [r["paid"] for r in before["orders"]] == [r["paid"] for r in after["orders"]]
    assert after["cash"] == before["cash"]
    assert after["market_change"] == 70000
    assert after["owners"][0]["federal_ira_basis"] == Decimal("16470.59")
    assert sum(after["account_balances"].values()) + after["cash"] == 220000


def test_limited_balance_and_conditional_exception_do_not_change_taxable_income():
    data = payload()
    data["orders"] = [dict(data["orders"][0], amount="200000.00")]
    result = calculate(data)
    row = result["orders"][0]
    assert row["paid"] == row["unfilled"] == 100000
    assert row["federal_taxable"] == 80000
    assert row["additional_tax"] == 8000
    data["orders"][0]["early_penalty_exception"] = True
    exempt = calculate(data)["orders"][0]
    assert exempt["federal_taxable"] == row["federal_taxable"]
    assert exempt["additional_tax"] == 0
