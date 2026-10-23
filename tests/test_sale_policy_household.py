"""Household targets include other accounts but authorize sales only in the selected account."""

from decimal import Decimal as D

from test_sale_policies import case_with, decision

from wealthlab.portfolio.cases import LotCase
from wealthlab.portfolio.engine import run


def test_other_account_concentration_is_visible_but_cannot_be_sold():
    """A zero target cannot authorize liquidation of a separate spouse account.

    Its 100 shares remain in both the concentration numerator and wealth denominator.
    """
    payload = case_with(decision("target_weight", "0"))
    payload["accounts"].append(dict(payload["accounts"][0], id="spouse", cash="0", owner="spouse"))
    payload["lots"].append(dict(payload["lots"][0], id="other", account_id="spouse"))
    result = run(LotCase.model_validate(payload))
    row = result["sale_decisions"][0]
    assert row["requested_units"] == 175
    assert row["sold_units"] == 75
    assert row["unfilled_units"] == 100
    assert row["weight_after"] == D(10000) / D(20995)
    assert result["lots"][0]["account_id"] == "spouse"


def test_same_day_manual_sale_precedes_cumulative_policy():
    payload = case_with(dict(decision(), date="2026-06-01"))
    result = run(LotCase.model_validate(payload))
    assert [trade["id"] for trade in result["executed_trades"]] == ["sale", "policy"]
    assert result["sale_decisions"][0]["sold_units"] == 25


def test_met_weight_target_does_not_charge_a_fee_or_sell():
    payload = case_with(decision("target_weight", "1", commission="500"))
    result = run(LotCase.model_validate(payload))
    assert result["sale_decisions"][0]["sold_units"] == 0
    assert result["transaction_costs"] == 5


def test_hifo_staged_target_excludes_new_high_basis_purchase():
    """The higher-basis new purchase is attractive to HIFO but is not an original lot."""
    payload = case_with(decision(selection="hifo"))
    sale = payload["trades"][0]
    purchase = dict(sale, id="new", action="buy", quantity="10", price="200", commission="0")
    payload["trades"].append(purchase)
    result = run(LotCase.model_validate(payload))
    assert result["disposals"][-1]["lot_id"] == "original"
    assert result["sale_decisions"][0]["sold_units"] == 25
    new_lot = next(lot for lot in result["lots"] if lot["id"] == "new")
    assert new_lot["quantity"] == "10"
