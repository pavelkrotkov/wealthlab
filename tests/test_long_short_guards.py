"""Unknown terms, dates and dishonest comparison capital block an economic conclusion."""

import pytest
from long_short_cases import batch, flat

from wealthlab.products.long_short_compare import compare
from wealthlab.products.long_short_inputs import LongShortCase
from wealthlab.products.long_short_run import run


@pytest.mark.parametrize(
    "changes",
    [
        dict(terms_confirmed=False),
        dict(short_factor="missing"),
        dict(long_multiple=5, short_multiple=5),
        dict(
            redemptions=[dict(id="draw", provenance="assumption", date="2026-01-15", amount=1000)]
        ),
    ],
)
def test_invalid_terms_and_redemption_timing_block(changes):
    case, market = flat()
    case = LongShortCase.model_validate(dict(case.model_dump(), **changes))
    with pytest.raises(ValueError):
        run(case, batch(market))


@pytest.mark.parametrize("indices", [[], [0, 0], [2]])
def test_empty_duplicate_or_unknown_paths_block(indices):
    case, market = flat()
    with pytest.raises(ValueError):
        run(case, batch(market), indices)


def test_different_starting_capital_cannot_be_ranked_as_a_paired_policy():
    case, market = flat()
    other = LongShortCase.model_validate(dict(case.model_dump(), opening_equity=200000))
    with pytest.raises(ValueError, match="same investor capital"):
        compare(case, other, batch(market))
