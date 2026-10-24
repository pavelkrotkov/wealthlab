"""Dated policies conserve capital and distinguish original units from value weights."""

from decimal import Decimal as D

import pytest

from wealthlab.portfolio.cases import LotCase
from wealthlab.portfolio.engine import run
from wealthlab.portfolio.example import synthetic


def decision(mode="original_fraction", fraction="0.5", **overrides):
    return dict(
        id="policy",
        provenance="assumption",
        date="2026-07-01",
        account_id="brokerage",
        security_id="STOCK",
        mode=mode,
        fraction=fraction,
        prices={"STOCK": "100"},
        **overrides,
    )


def case_with(*policies):
    payload = synthetic().model_dump(mode="json")
    payload["sale_policies"] = list(policies)
    return payload


def test_staged_target_counts_manual_sales_and_is_idempotent():
    """A second date with the same cumulative target must not sell another fraction.

    The opening manual sale already counts toward the policy's 50 original shares.
    """
    first = decision()
    second = dict(first, id="second", date="2026-08-01")
    result = run(LotCase.model_validate(case_with(first, second)))
    assert [row["sold_units"] for row in result["sale_decisions"]] == [25, 0]
    assert result["gross_wealth"] == 10995
    assert result["concentration"]["securities"][0]["original_fraction_sold"] == D("0.5")
    assert result["lots"][0]["federal_basis"] == "2500.00"


def test_weight_target_includes_cash_and_fee_instead_of_original_share_fraction():
    """The fee lowers gross wealth to 10985; 5492.50 in stock is exactly one half.

    The remaining 54.925 shares differ from a 50-share original-share target.
    """
    payload = case_with(decision("target_weight", commission="10"))
    result = run(LotCase.model_validate(payload))
    row = result["sale_decisions"][0]
    assert row["sold_units"] == D("20.075")
    assert row["weight_after"] == D("0.5")
    assert result["gross_wealth"] == 10985
    assert result["transaction_costs"] == 15
    assert result["concentration"]["securities"][0]["original_units_sold"] == D("45.075")


def test_closing_prices_and_future_policies_cannot_change_earlier_decision():
    """A tenfold terminal mark and later sale cannot leak into the July decision."""
    payload = case_with(decision("target_weight"))
    expected = run(LotCase.model_validate(payload))["sale_decisions"][0]
    payload["closing_prices"]["STOCK"] = "1000"
    payload["sale_policies"].append(
        dict(decision("sell_all", None), id="future", date="2026-12-01", prices={"STOCK": "900"})
    )
    result = run(LotCase.model_validate(payload))
    assert result["sale_decisions"][0] == expected
    assert result["executed_trades"][-1]["price"] == "900"


@pytest.mark.parametrize("mode, expected", [("retain", 0), ("sell_all", 75)])
def test_retain_and_immediate_liquid_sale(mode, expected):
    result = run(LotCase.model_validate(case_with(decision(mode, None))))
    assert result["sale_decisions"][0]["sold_units"] == expected
    assert result["gross_wealth"] == 10995
