"""Partial replacement lots and later exits conserve cost while tax deferral reverses."""

from decimal import Decimal as D

from test_wash_sales import wash_case

from wealthlab.portfolio.cases import LotCase
from wealthlab.portfolio.engine import run


def test_more_replacement_shares_split_without_spreading_basis():
    payload = wash_case(quantity="150").model_dump(mode="json")
    payload["accounts"][1]["cash"] = "1500"
    result = run(LotCase.model_validate(payload))
    assert sorted((D(lot["quantity"]), D(lot["federal_basis"])) for lot in result["lots"]) == [
        (D(50), D(400)),
        (D(100), D(1050)),
    ]
    assert sum(D(lot["economic_basis"]) for lot in result["lots"]) == 1200
    assert sum(D(lot["nj_basis"]) for lot in result["lots"]) == 1200
    assert result["disposals"][0]["federal_recognized_gain"] == 0


def test_later_exit_realizes_deferred_loss_but_not_a_new_economic_loss():
    """The replacement earns $100 economically while releasing the old $250 loss.

    Counting its $150 tax loss as new market loss would double-count the deferral.
    """
    payload = wash_case().model_dump(mode="json")
    payload["trades"].append(
        dict(
            payload["trades"][1],
            id="exit",
            action="sell",
            date="2026-09-01",
            price="9",
        )
    )
    result = run(LotCase.model_validate(payload))
    first, last = result["disposals"]
    assert first["economic_pnl"] == -250
    assert last["economic_pnl"] == 100
    assert last["federal_recognized_gain"] == -150
    assert last["nj_gross_gain"] == 100
    assert result["closing_cash"] == 2850
    assert not result["lots"]


def test_prior_replacement_split_preserves_original_share_counts():
    payload = wash_case().model_dump(mode="json")
    payload["as_of"] = "2026-06-01"
    payload["trades"] = payload["trades"][:1]
    payload["lots"].append(
        dict(
            payload["lots"][0],
            id="prior",
            account_id="replacement_account",
            quantity="150",
            acquired="2026-05-15",
            federal_holding_start="2026-05-15",
            liquid_after="2026-05-15",
            federal_basis="1200",
            nj_basis="1200",
            economic_basis="1200",
        )
    )
    result = run(LotCase.model_validate(payload))
    assert result["disposals"][0]["federal_wash_disallowed"] == 250
    row = result["concentration"]["securities"][0]
    assert row["original_units_sold"] == 100
    assert row["original_units"] == 250
    assert row["remaining_units"] == 150
