"""Sampling intervals stay nondegenerate at zero/all success; pairing requires identity."""

import pytest

from wealthlab.markets.household_report import wilson
from wealthlab.markets.household_run import paired


def test_wilson_matches_independent_published_boundary_algebra():
    lower, upper = wilson(100, 100)
    assert lower == pytest.approx(0.9630065018)
    assert upper == pytest.approx(1)
    zero = wilson(0, 100)
    assert zero[0] == pytest.approx(0)
    assert zero[1] == pytest.approx(0.0369934982)


def test_pairing_rejects_different_realized_batch_identity():
    with pytest.raises(ValueError, match="same batch"):
        paired(dict(batch_id="left", indices=[0]), dict(batch_id="right", indices=[0]))
