"""Independent compounding and model moments constrain the seeded path engine.

Annual arithmetic expectation is not median compound growth: the log drift
must account for volatility. The large seeded one-year sample checks the
expectation within sampling tolerance; a separate flattened log-shock sample
checks joint correlation without confusing price and log-return moments.
Zero volatility must reduce to the exact deterministic compounding convention.
Cash yield is tested at zero mark growth so reinvestment cannot hide in a
geometric formula, and accidental edits cannot corrupt a paired batch.
"""

import numpy as np
import pytest

from wealthlab.markets.example import synthetic
from wealthlab.markets.inputs import MarketCase
from wealthlab.markets.paths import generate
from wealthlab.markets.report import summarize


def test_deterministic_marks_compound_to_the_declared_annual_growth():
    batch = generate(synthetic("deterministic"))
    terminal = summarize(batch)["mark_indices"][0, -1]
    np.testing.assert_allclose(terminal, 100 * np.array([1.05, 1.01, 1.05]) ** 10)
    assert batch.mark_returns.shape == (1, 120, 3)


def test_cash_yield_does_not_turn_into_price_growth_or_interest():
    data = synthetic("deterministic").model_dump(mode="json")
    for asset in data["assets"]:
        asset["expected_annual_mark_return"] = 0
    data["expected_annual_inflation"] = 0
    report = summarize(generate(MarketCase.model_validate(data)))
    np.testing.assert_allclose(report["mark_indices"][0, -1], [100, 100, 100])
    np.testing.assert_allclose(report["separate_cash_yields"][0, -1], [20, 30, 0])
    np.testing.assert_allclose(report["real_buy_hold"][0, -1], [120, 130, 100])


def test_monte_carlo_preserves_one_year_expected_mark_growth():
    data = synthetic().model_dump(mode="json")
    data.update(end="2028-01-01", paths=5000)
    batch = generate(MarketCase.model_validate(data))
    terminal = np.prod(1 + batch.mark_returns, axis=1)
    np.testing.assert_allclose(terminal.mean(axis=0), [1.05, 1.01, 1.05], atol=0.025)


def test_actual_log_shocks_match_the_declared_joint_correlation():
    case = synthetic()
    batch = generate(case)
    joint = np.concatenate(
        (np.log1p(batch.mark_returns), np.log1p(batch.inflation)[:, :, None]), axis=2
    )
    observed = np.corrcoef(joint.reshape(-1, 4), rowvar=False)
    np.testing.assert_allclose(observed, case.correlation, atol=0.025)


def test_seeded_batches_reproduce_and_readonly_arrays_reject_accidental_edits():
    first, second = generate(synthetic()), generate(synthetic())
    assert first.metadata["batch_id"] == second.metadata["batch_id"]
    np.testing.assert_array_equal(first.mark_returns, second.mark_returns)
    with pytest.raises(ValueError, match="read-only"):
        first.mark_returns[0, 0, 0] = 0


def test_zero_volatility_monte_carlo_is_the_deterministic_path():
    data = synthetic().model_dump(mode="json")
    data["annual_inflation_volatility"] = 0
    for asset in data["assets"]:
        asset["annual_volatility"] = 0
    case = MarketCase.model_validate(data)
    batch = generate(case)
    data.update(mode="deterministic", paths=1)
    expected = generate(MarketCase.model_validate(data))
    np.testing.assert_allclose(batch.mark_returns[0], expected.mark_returns[0])
    np.testing.assert_array_equal(batch.mark_returns[0], batch.mark_returns[-1])
