"""Validate opening dates, identities, integer shares and representable basis before funding."""

import pytest

from wealthlab.products.option_engine import run
from wealthlab.products.option_inputs import OptionCase
from wealthlab.products.option_purchase_example import unit_plan


@pytest.mark.parametrize(
    "update",
    [
        {"shares": "1.5"},
        {"shares": True},
        {"shares": -1},
        {"date": "2026-01-31"},
        {"provenance": "unresolved"},
        {"id": "stock_call"},
        {"id": "exercise_stock_call"},
        {"id": "complete_unwind"},
    ],
)
def test_unsupported_opening_purchase_is_rejected_before_native_trading(update):
    data = unit_plan().case.model_dump(mode="json")
    data["opening_stock_purchase"].update(update)
    with pytest.raises(ValueError):
        run(OptionCase.model_validate(data))


def test_unrepresentable_purchase_basis_is_rejected_before_funding():
    data = unit_plan().case.model_dump(mode="json")
    data["marks"][0]["stock"] = "9999999999999999"
    with pytest.raises(ValueError):
        run(OptionCase.model_validate(data))
