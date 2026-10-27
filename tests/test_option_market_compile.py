"""Only realized prices set marks; future shocks cannot alter earlier observations."""

import pytest

from tests.option_market_cases import change, flat
from wealthlab.household.projection import project
from wealthlab.markets.household_compile import compile_marks
from wealthlab.markets.household_execution import Execution


def test_stale_compiled_option_price_cannot_enter_actual_household_execution():
    scenario, batch, binding = flat()
    compiled = compile_marks(scenario, batch, binding, 0)
    stale = change(
        compiled, lambda data: data["option_plan"]["case"]["marks"][-1].update(stock="101")
    )
    with pytest.raises(ValueError, match="stale marks"):
        project(stale, market=Execution(stale, batch, binding, 0))
