"""Only actual plans and supported physical-price observations enter native cash execution."""

import pytest
from drilling_market_cases import edited

from wealthlab.markets.household_run import run
from wealthlab.markets.paths import generate


def test_total_return_marks_cannot_silently_replace_actual_price_only_receipts():
    case = edited(lambda data: data["market"].update(return_convention="total_return_reinvested"))
    with pytest.raises(ValueError, match="separate price-plus-cash"):
        run(case.household, generate(case.market), case.binding)
