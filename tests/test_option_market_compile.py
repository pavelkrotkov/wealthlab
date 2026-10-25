"""Only realized prices set marks; future shocks cannot alter earlier observations."""

from decimal import Decimal

import pytest

from tests.option_market_cases import change, flat
from wealthlab.household.projection import project
from wealthlab.markets.household_compile import compile_marks
from wealthlab.markets.household_execution import Execution
from wealthlab.markets.household_run import run
from wealthlab.markets.option_example import synthetic
from wealthlab.markets.paths import generate


def test_compiler_replaces_every_mark_with_explicit_fixed_valuation_assumptions():
    scenario, batch, binding = flat()
    compiled = compile_marks(scenario, batch, binding, 0)
    assert compiled.option_plan is not None
    assert binding.options is not None
    case = compiled.option_plan.case
    assert len(case.marks) == 13
    assert {mark.stock for mark in case.marks} == {Decimal(100)}
    assert {mark.index for mark in case.marks} == {Decimal(100)}
    assert all("no option quotes" in mark.source for mark in case.marks)
    assert case.marks[-1].stock_vol == binding.options.stock_vol


def test_stale_compiled_option_price_cannot_enter_actual_household_execution():
    scenario, batch, binding = flat()
    compiled = compile_marks(scenario, batch, binding, 0)
    stale = change(
        compiled, lambda data: data["option_plan"]["case"]["marks"][-1].update(stock="101")
    )
    with pytest.raises(ValueError, match="stale marks"):
        project(stale, market=Execution(stale, batch, binding, 0))


@pytest.mark.parametrize("mode", ["deterministic", "monte_carlo", "historical", "stress"])
def test_all_market_modes_keep_model_valuations_distinct_from_quote_history(mode):
    scenario, market, binding = synthetic(mode)
    result = run(scenario, generate(market), binding, indices=[0])
    audit = result["details"][0]["rows"][-1]["option_mark_audit"]
    assert audit
    assert result["outcomes"][0]["issuer_concentration_complete"] is False
