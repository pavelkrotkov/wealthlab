"""Eligibility, household purchase history and liquidity constrain harvesting decisions."""

import pytest
from test_harvest_comparison import harvest_case

from wealthlab.portfolio.cases import LotCase
from wealthlab.portfolio.engine import run


@pytest.mark.parametrize("change", ["no_loss", "locked", "costs"])
def test_no_executable_loss_produces_a_zero_comparison(change):
    payload = harvest_case()
    policy = payload["harvest_policies"][0]
    if change == "no_loss":
        policy["prices"]["STOCK"] = "12"
    elif change == "locked":
        payload["lots"][0]["liquid_after"] = "2027-01-01"
    else:
        policy["commission_per_trade"] = "500"
    result = run(LotCase.model_validate(payload))
    assert result["harvest_decisions"][0]["sold_units"] == 0
    assert result["harvest_comparison"]["holding"]["tax_adjusted_difference"] == 0


def test_recent_household_loss_blocks_repurchasing_the_replacement_group():
    payload = harvest_case()
    original = payload["lots"][0]
    payload["lots"].append(
        dict(
            original,
            id="prior_etf",
            security_id="ETF",
            quantity="10",
            federal_basis="100",
            nj_basis="100",
        )
    )
    payload["trades"] = [
        dict(
            id="prior_loss",
            provenance="assumption",
            date="2026-05-20",
            account_id="brokerage",
            security_id="ETF",
            action="sell",
            quantity="10",
            price="5",
            commission="0",
        )
    ]
    result = run(LotCase.model_validate(payload))
    assert "blocked" in result["harvest_decisions"][0]["status"]
    assert not result["harvest_sales"]


def test_later_manual_purchase_can_wash_an_earlier_harvest():
    """The decision cannot anticipate this buy, but final tax recognition must observe it.

    A distinct immediate replacement does not make later household repurchases safe.
    """
    payload = harvest_case()
    payload["trades"] = [
        dict(
            id="later_buy",
            provenance="assumption",
            date="2026-06-20",
            account_id="brokerage",
            security_id="STOCK",
            action="buy",
            quantity="100",
            price="7.5",
            commission="0",
        )
    ]
    result = run(LotCase.model_validate(payload))
    assert result["harvest_loss_summary"]["federal_wash_deferred"] == 250
    assert result["harvest_loss_summary"]["federal_recognized_gain"] == 0
    assert result["harvest_comparison"]["holding"]["total_tax_saving"] == 0


@pytest.mark.parametrize(
    "change,message",
    [
        ({"replacement_eligible": False}, "Confirm replacement"),
        ({"replacement_id": "STOCK"}, "distinct"),
        ({"replacement_id": "missing"}, "configured security"),
    ],
)
def test_replacement_eligibility_cannot_be_inferred(change, message):
    payload = harvest_case()
    payload["harvest_policies"][0].update(change)
    with pytest.raises(ValueError, match=message):
        run(LotCase.model_validate(payload))
