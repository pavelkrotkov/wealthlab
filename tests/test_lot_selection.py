"""Selection policies choose different lots without overselling or financing purchases."""

from decimal import Decimal as D

import pytest

from wealthlab.portfolio.book import Book
from wealthlab.portfolio.cases import LotCase
from wealthlab.portfolio.engine import run
from wealthlab.portfolio.example import synthetic
from wealthlab.portfolio.orders import Trade


@pytest.mark.parametrize("selection", ["fifo", "hifo", "specific"])
def test_selection_and_exact_share_limit(selection):
    payload = synthetic().model_dump(mode="json")
    payload["lots"].append(
        dict(payload["lots"][0], id="higher", federal_basis="15000", acquired="2021-01-01")
    )
    payload["trades"][0].update(
        selection=selection, lot_ids=["higher"] if selection == "specific" else []
    )
    result = run(LotCase.model_validate(payload))
    expected = "original" if selection == "fifo" else "higher"
    assert result["disposals"][0]["lot_id"] == expected
    assert sum(D(lot["quantity"]) for lot in result["lots"]) == 175


def test_overselling_and_unfunded_purchase_do_not_mutate_book():
    case = synthetic()
    book = Book(case)
    bad_sale = case.trades[0].model_copy(update={"quantity": D(101)})
    with pytest.raises(ValueError, match="exceeds"):
        book.trade(bad_sale)
    bad_buy = Trade.model_validate(
        dict(
            case.trades[0].model_dump(),
            id="purchase",
            action="buy",
            quantity=D(20),
        )
    )
    with pytest.raises(ValueError, match="exceeds"):
        book.trade(bad_buy)
    assert book.cash["brokerage"] == 1000
    assert book.lots["original"].quantity == 100
    assert not book.disposals
    assert not book.history
