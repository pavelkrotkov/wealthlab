"""Generated history and directly supplied batches both enforce full monthly coverage.

The UI constructs a validated MarketCase before generate(), so extending the
historical horizon without more observations is already rejected there. The
public household runner additionally checks dates/axes on a supplied PathBatch
instead of relying on metadata or allowing raw NumPy indexing errors.
"""

import pytest

from wealthlab.markets.household_example import synthetic
from wealthlab.markets.inputs import MarketCase


def test_extended_historical_input_is_rejected_before_ui_generation():
    _, market, _ = synthetic("historical")
    data = market.model_dump(mode="json")
    data["end"] = "2029-01-01"
    with pytest.raises(ValueError, match="Historical coverage"):
        MarketCase.model_validate(data)
