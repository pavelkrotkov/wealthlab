"""All four path modes have executable household inputs, with invented replay provenance."""

import pytest

from wealthlab.markets.household_example import synthetic
from wealthlab.markets.household_run import run
from wealthlab.markets.paths import generate


def test_invented_historical_replay_runs_actual_lots_with_disclosed_provenance():
    case, market, binding = synthetic("historical")
    batch = generate(market)
    result = run(case, batch, binding)
    rows = result["details"][0]["rows"]
    assert batch.metadata["historical_synthetic"]
    assert "synthetic assumptions" in market.historical.source
    assert rows[0]["market_cash_yield"] > 0
    assert result["aggregate"]["monte_carlo_95_wilson"] is None
    assert len(rows) == 24


@pytest.mark.parametrize(
    "stress", ["early_crash", "prolonged_inflation", "concentration_loss", "illiquidity"]
)
def test_each_named_stress_has_valid_actual_household_bindings(stress):
    _, market, _ = synthetic("stress", stress)
    batch = generate(market)
    assert batch.metadata["mode"] == "stress"
    assert market.shocks
