"""All market modes execute native QOF economics; invented replay is never quote history."""

import pytest

from wealthlab.markets.household_run import run
from wealthlab.markets.paths import generate
from wealthlab.markets.qoz_example import synthetic


@pytest.mark.parametrize("mode", ["deterministic", "monte_carlo", "historical", "stress"])
def test_native_qof_runs_on_each_market_mode_with_explicit_source_and_contract_audit(mode):
    case, market, binding = synthetic(mode)
    result = run(case, generate(market), binding, indices=[0])
    final = result["details"][0]["rows"][-1]
    assert final["qoz_audit"]["calls"][0]["funded"] > 0
    assert result["batch_id"]
    assert "no QOF quotes" in result["binding"]["qoz"]["return_source_description"]
    if mode == "historical":
        assert market.historical.synthetic is True
        assert "invented" in market.historical.source
