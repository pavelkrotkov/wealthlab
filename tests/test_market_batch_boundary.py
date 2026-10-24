"""Generated history and directly supplied batches both enforce full monthly coverage.

The UI constructs a validated MarketCase before generate(), so extending the
historical horizon without more observations is already rejected there. The
public household runner additionally checks dates/axes on a supplied PathBatch
instead of relying on metadata or allowing raw NumPy indexing errors.
"""

from dataclasses import replace

import pytest

from tests.market_household_cases import flat
from wealthlab.markets.household_example import synthetic
from wealthlab.markets.household_run import run
from wealthlab.markets.inputs import MarketCase
from wealthlab.markets.paths import generate


def test_extended_historical_input_is_rejected_before_ui_generation():
    _, market, _ = synthetic("historical")
    data = market.model_dump(mode="json")
    data["end"] = "2029-01-01"
    with pytest.raises(ValueError, match="Historical coverage"):
        MarketCase.model_validate(data)


@pytest.mark.parametrize("field", ["mark_returns", "cash_yields", "inflation", "locked", "dates"])
def test_direct_batch_cannot_use_metadata_to_hide_a_missing_month(field):
    case, market, binding = flat()
    batch = generate(market)
    values = getattr(batch, field)
    truncated = (
        values[:, :-1] if field in {"mark_returns", "cash_yields", "inflation"} else values[:-1]
    )
    invalid = replace(batch, **{field: truncated})
    with pytest.raises(ValueError, match="cover every household month"):
        run(case, invalid, binding)


@pytest.mark.parametrize("selection", [(0,), (0, 0), (0, 0, 0)])
def test_direct_batch_marks_need_the_actual_three_axes(selection):
    case, market, binding = flat()
    batch = generate(market)
    invalid = replace(batch, mark_returns=batch.mark_returns[selection])
    with pytest.raises(ValueError, match="path, month and factor axes"):
        run(case, invalid, binding)
