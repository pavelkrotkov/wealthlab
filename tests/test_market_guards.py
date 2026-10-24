"""Reject impossible correlation, unresolved assumptions and duplicate return streams."""

import pytest

from wealthlab.markets.example import synthetic
from wealthlab.markets.inputs import MarketCase


@pytest.mark.parametrize(
    "matrix",
    [
        [[1, 0.9, 0.9, 0], [0.9, 1, -0.9, 0], [0.9, -0.9, 1, 0], [0, 0, 0, 1]],
        [[1, 0.2], [0.1, 1]],
        [[1, 0, 0, 0], [0.1, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]],
    ],
)
def test_invalid_joint_correlation_blocks_generation(matrix):
    data = synthetic().model_dump(mode="json")
    data["correlation"] = matrix
    with pytest.raises(ValueError, match="Correlation"):
        MarketCase.model_validate(data)


def test_total_return_and_cash_yields_cannot_both_claim_the_same_distribution():
    data = synthetic().model_dump(mode="json")
    data["return_convention"] = "total_return_reinvested"
    with pytest.raises(ValueError, match="cannot also distribute"):
        MarketCase.model_validate(data)


def test_resource_bound_prevents_an_unbounded_local_allocation():
    data = synthetic().model_dump(mode="json")
    data["paths"] = 5000
    with pytest.raises(ValueError, match="2 million"):
        MarketCase.model_validate(data)


def test_unresolved_asset_assumptions_cannot_generate_a_result():
    data = synthetic().model_dump(mode="json")
    data["assets"][0]["provenance"] = "unresolved"
    with pytest.raises(ValueError, match="Resolve critical"):
        MarketCase.model_validate(data)
