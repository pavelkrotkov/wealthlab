"""Lot quantity, jurisdiction basis and cash conservation with independently known values."""

from decimal import Decimal as D

from wealthlab.portfolio.cases import LotCase
from wealthlab.portfolio.engine import run
from wealthlab.portfolio.example import synthetic


def test_partial_sale_preserves_separate_basis_and_costs():
    result = run(synthetic())
    assert result["closing_cash"] == 3495
    assert result["gross_wealth"] == 10995
    sold = result["disposals"][0]
    assert (sold["federal_gross_gain"], sold["nj_gross_gain"]) == (1245, 995)
    remaining = result["lots"][0]
    assert D(remaining["quantity"]) == 75
    assert D(remaining["federal_basis"]) + sold["federal_basis"] == 5000
    assert D(remaining["nj_basis"]) + sold["nj_basis"] == 6000


def test_purchase_uses_cash_and_includes_commission_in_basis():
    payload = synthetic().model_dump(mode="json")
    payload["trades"].append(
        dict(
            payload["trades"][0],
            id="purchase",
            action="buy",
            quantity="5",
            date="2026-06-02",
        )
    )
    result = run(LotCase.model_validate(payload))
    assert result["closing_cash"] == 2990
    assert result["gross_wealth"] == 10990
    assert result["lots"][1]["id"] == "purchase"
    assert D(result["lots"][1]["federal_basis"]) == 505
    assert result["transaction_costs"] == 10
