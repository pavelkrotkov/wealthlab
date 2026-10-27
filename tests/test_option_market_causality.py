"""Future paths do not rewrite prior prices; unsupported precision/quote periods fail."""

import pytest

from tests.option_market_cases import change, flat
from wealthlab.markets.household_inputs import HouseholdBinding
from wealthlab.markets.household_run import run


def test_option_account_cannot_keep_stale_prices_when_another_market_binding_runs():
    scenario, batch, binding = flat()
    data = binding.model_dump(mode="json")
    data["options"] = None
    with pytest.raises(ValueError, match="Bind the complete actual option account"):
        run(scenario, batch, HouseholdBinding.model_validate(data))
    no_plan = change(scenario, lambda data: data.update(option_plan=None))
    with pytest.raises(ValueError, match="requires an actual household option plan"):
        run(no_plan, batch, binding)
