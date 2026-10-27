"""All four path modes have executable household inputs, with invented replay provenance."""

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
