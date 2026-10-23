"""Entitlement, cash availability and tax recognition cannot be interchanged."""

from decimal import Decimal as D

from distribution_cases import distribution_case, trade

from wealthlab.portfolio.cases import LotCase
from wealthlab.portfolio.engine import run


def test_ex_date_sale_keeps_the_later_receipt_and_does_not_duplicate_it():
    payload = distribution_case()
    payload["trades"] = [trade("sell", "2026-06-01")]
    result = run(LotCase.model_validate(payload))
    assert result["closing_cash"] == result["gross_wealth"] == 2100
    assert result["distribution_receivable"] == 0
    annual = result["annual_tax_comparison"][0]
    assert annual["distribution_federal"] == dict(dividends=100, qualified_dividends=100)
    assert annual["distribution_nj"] == dict(dividends=100)


def test_ex_date_purchase_does_not_receive_that_distribution():
    payload = distribution_case()
    payload["lots"] = []
    payload["trades"] = [trade("buy", "2026-06-01")]
    result = run(LotCase.model_validate(payload))
    assert not result["distributions"]
    assert result["closing_cash"] == 0
    assert result["gross_wealth"] == 1000


def test_unpaid_distribution_is_a_receivable_not_available_cash():
    """An earned $100 distribution increases assets while cash stays at $1,000.

    It cannot finance a $1,050 purchase before payment or enter annual cash-method
    income before its configured recognition date.
    """
    payload = distribution_case()
    payload["end"] = "2026-06-10"
    result = run(LotCase.model_validate(payload))
    assert result["closing_cash"] == 1000
    assert result["distribution_receivable"] == 100
    assert result["gross_wealth"] == 2100
    assert not result["annual_tax_comparison"][0]["distribution_federal"]
    payload["trades"] = [trade("buy", "2026-06-05", qty="105")]
    import pytest

    with pytest.raises(ValueError, match="available account cash"):
        run(LotCase.model_validate(payload))


def test_retirement_receipts_remain_inside_the_account_without_current_income_tax():
    payload = distribution_case()
    payload["accounts"][0]["wrapper"] = "roth_ira"
    result = run(LotCase.model_validate(payload))
    assert result["closing_cash"] == 1100
    assert result["annual_tax_comparison"][0]["incremental_liability"] == 0


def test_per_account_rounding_conserves_tiny_lot_entitlements():
    """Five six-tenths-of-a-cent entitlements total three cents, not five.

    Cumulative rounding must also avoid a negative final-lot allocation.
    """
    payload = distribution_case()
    lot = payload["lots"][0]
    payload["lots"] = [dict(lot, id=f"lot_{index}", quantity="0.006") for index in range(5)]
    result = run(LotCase.model_validate(payload))
    assert result["closing_cash"] == D("1000.03")
    assert sum(row["amount"] for row in result["distributions"]) == D("0.03")
    assert all(row["amount"] >= 0 for row in result["distributions"])
