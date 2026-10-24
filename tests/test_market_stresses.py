"""Stress overlays change the intended month without resampling the paired base.

A crash multiplies the affected growth factor, not its percentage return.
A liquidity lock preserves marks, while a total loss preserves zero units of
value despite later positive return observations. Inflation changes only the
specified regime, so comparisons share all other realized observations.
"""

import numpy as np
import pytest

from wealthlab.markets.example import synthetic
from wealthlab.markets.inputs import MarketCase
from wealthlab.markets.paths import generate
from wealthlab.markets.report import summarize
from wealthlab.markets.stresses import events


def test_seeded_crash_preserves_every_unshocked_market_and_inflation_observation():
    case = synthetic()
    base = generate(case)
    data = case.model_dump(mode="json")
    data.update(mode="stress", stress_base="monte_carlo", shocks=events(case, "early_crash"))
    stressed = generate(MarketCase.model_validate(data))
    np.testing.assert_array_equal(base.mark_returns[:, 1:], stressed.mark_returns[:, 1:])
    np.testing.assert_array_equal(base.inflation, stressed.inflation)
    np.testing.assert_allclose(
        1 + stressed.mark_returns[:, 0, 0], (1 + base.mark_returns[:, 0, 0]) * 0.6
    )


def test_illiquidity_retains_market_value_and_locks_only_the_named_period():
    base = generate(synthetic("deterministic"))
    locked = generate(synthetic("stress", "illiquidity"))
    np.testing.assert_array_equal(base.mark_returns, locked.mark_returns)
    assert locked.locked[:36].all()
    assert not locked.locked[36:].any()


def test_prolonged_inflation_compounds_to_the_named_three_year_rate():
    batch = generate(synthetic("stress", "prolonged_inflation"))
    assert np.prod(1 + batch.inflation[0, :36]) == pytest.approx(1.1**3)


def test_a_total_asset_loss_cannot_resurrect_the_mark_index():
    data = synthetic("stress").model_dump(mode="json")
    data["shocks"] = [dict(name="total_loss", month=0, mark_shocks={"employer": -1})]
    report = summarize(generate(MarketCase.model_validate(data)))
    assert np.all(report["mark_indices"][0, :, 2] == 0)
    assert report["maximum_mark_drawdown"][0, 2] == 1


def test_concentration_loss_changes_only_the_first_named_risky_factor():
    base = generate(synthetic("deterministic"))
    stressed = generate(synthetic("stress", "concentration_loss"))
    assert 1 + stressed.mark_returns[0, 0, 0] == pytest.approx(
        (1 + base.mark_returns[0, 0, 0]) * 0.25
    )
    np.testing.assert_array_equal(base.mark_returns[:, :, 1:], stressed.mark_returns[:, :, 1:])
