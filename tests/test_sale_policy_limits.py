"""Unavailable shares, ambiguous inputs and new purchases cannot masquerade as originals."""

import pytest
from test_sale_policies import case_with, decision

from wealthlab.portfolio.cases import LotCase
from wealthlab.portfolio.engine import run


def test_locked_shares_report_unfilled_target_without_forced_sale():
    payload = case_with(decision())
    payload["trades"] = []
    payload["lots"][0]["liquid_after"] = "2027-01-01"
    result = run(LotCase.model_validate(payload))
    assert result["sale_decisions"][0]["sold_units"] == 0
    assert result["sale_decisions"][0]["unfilled_units"] == 50
    assert result["gross_wealth"] == 11000


def test_new_purchases_do_not_replace_original_share_target():
    payload = case_with(decision())
    sale = dict(payload["trades"][0], quantity="100")
    purchase = dict(sale, id="new", action="buy", quantity="50", commission="0")
    payload["trades"] = [sale, purchase]
    result = run(LotCase.model_validate(payload))
    assert result["sale_decisions"][0]["sold_units"] == 0
    assert result["lots"][0]["id"] == "new"


def test_cost_exceeding_available_proceeds_does_not_destroy_cash():
    payload = case_with(decision("sell_all", None, commission="8000"))
    result = run(LotCase.model_validate(payload))
    assert result["sale_decisions"][0]["unfilled_units"] == 75
    assert result["transaction_costs"] == 5


@pytest.mark.parametrize(
    "change, message",
    [
        ({"id": "sale"}, "distinct"),
        ({"date": "2027-01-01"}, "dates"),
        ({"provenance": "unresolved"}, "Resolve"),
        ({"prices": {}}, "current price"),
        ({"account_id": "missing"}, "reference"),
        ({"fraction": None}, "Supply fraction"),
    ],
)
def test_ambiguous_policy_inputs_block_before_replay(change, message):
    payload = case_with(dict(decision(), **change))
    with pytest.raises(ValueError, match=message):
        run(LotCase.model_validate(payload))
