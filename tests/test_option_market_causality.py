"""Future paths do not rewrite prior prices; unsupported precision/quote periods fail."""

import pytest

from tests.option_market_cases import change, flat
from wealthlab.markets.household_compile import compile_marks
from wealthlab.markets.household_inputs import HouseholdBinding
from wealthlab.markets.household_run import run
from wealthlab.markets.inputs import MarketCase
from wealthlab.markets.option_example import synthetic
from wealthlab.markets.paths import generate


def test_later_shock_cannot_change_earlier_compiled_option_spots():
    scenario, market, binding = synthetic()
    data = market.model_dump(mode="json")
    baseline = compile_marks(scenario, generate(market), binding, 0)
    data.update(
        mode="stress", shocks=[dict(name="later", month=6, mark_shocks=dict(stock=-0.5, index=0.2))]
    )
    shocked = compile_marks(scenario, generate(MarketCase.model_validate(data)), binding, 0)
    assert baseline.option_plan is not None
    assert shocked.option_plan is not None
    prior = lambda case: [(m.date, m.stock, m.index) for m in case.option_plan.case.marks[:7]]  # noqa: E731
    assert prior(baseline) == prior(shocked)
    assert baseline.option_plan.case.marks[-1].stock != shocked.option_plan.case.marks[-1].stock


def test_spot_precision_writeoff_cannot_create_an_invented_liquidation_price():
    scenario, market, binding = synthetic()
    data = market.model_dump(mode="json")
    data.update(
        mode="stress",
        shocks=[dict(name="writeoff", month=0, mark_shocks=dict(stock=-0.99999999999))],
    )
    with pytest.raises(ValueError, match="spot rounded to zero"):
        run(scenario, generate(MarketCase.model_validate(data)), binding)


def test_option_account_cannot_keep_stale_prices_when_another_market_binding_runs():
    scenario, batch, binding = flat()
    data = binding.model_dump(mode="json")
    data["options"] = None
    with pytest.raises(ValueError, match="Bind the complete actual option account"):
        run(scenario, batch, HouseholdBinding.model_validate(data))
    no_plan = change(scenario, lambda data: data.update(option_plan=None))
    with pytest.raises(ValueError, match="requires an actual household option plan"):
        run(no_plan, batch, binding)
