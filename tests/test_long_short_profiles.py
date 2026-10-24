"""All projection modes share economic mechanics and explicitly synthetic history."""

import pytest

from wealthlab.markets.inputs import MarketCase
from wealthlab.markets.paths import generate
from wealthlab.products.long_short_compare import compare
from wealthlab.products.long_short_example import synthetic
from wealthlab.products.long_short_inputs import LongShortCase


@pytest.mark.parametrize("mode", ["deterministic", "monte_carlo", "historical", "stress"])
def test_each_mode_runs_paired_policies_without_regenerating_paths(mode):
    source = synthetic(mode)
    market = MarketCase.model_validate(source["market"])
    batch = generate(market)
    result = compare(
        LongShortCase.model_validate(source["sleeve"]),
        LongShortCase.model_validate(source["reference"]),
        batch,
        iter([0]),
    )
    assert (
        result["sleeve"]["batch_id"]
        == result["reference"]["batch_id"]
        == batch.metadata["batch_id"]
    )
    assert result["sleeve"]["indices"] == result["reference"]["indices"] == [0]
    assert result["sleeve"]["case"] == source["sleeve"]
    assert all(r["financing_loan"] == 0 for r in result["reference"]["details"][0]["rows"])


def test_exhausted_redemption_does_not_erase_future_requests_or_accrue_manager_fees():
    source = synthetic()
    data = source["sleeve"]
    data["redemptions"] = [
        dict(id="exit", provenance="assumption", date="2026-01-31", amount=1000000),
        dict(id="again", provenance="assumption", date="2026-02-28", amount=1000),
    ]
    case = LongShortCase.model_validate(data)
    from wealthlab.products.long_short_run import run

    rows = run(case, generate(MarketCase.model_validate(source["market"])))["details"][0]["rows"]
    assert rows[0]["closed"]
    assert rows[1]["redemption_unfilled"] == 1000
    assert rows[1]["manager_fee"] == rows[1]["borrow_cost"] == 0
