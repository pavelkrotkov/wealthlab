"""Bindings must replace known source schedules and preserve requested exposure."""

import pytest
from sleeve_market_cases import baseline

from wealthlab.household.scenario import Scenario
from wealthlab.markets.household_run import run
from wealthlab.markets.paths import generate


@pytest.mark.parametrize("mutation", ["unknown", "duplicate", "confirmation", "factor"])
def test_bad_sleeve_market_binding_blocks_before_execution(mutation):
    household, market, binding = baseline()
    data, terms = household.model_dump(mode="json"), binding.model_dump(mode="json")
    if mutation == "unknown":
        terms["sleeves"] = ["missing"]
    elif mutation == "duplicate":
        terms["sleeves"] = ["sleeve", "sleeve"]
    elif mutation == "confirmation":
        terms["replace_sleeve_observations_confirmed"] = False
    else:
        data["sleeve_plan"]["sleeves"][0]["case"]["long_factor"] = "missing"
    with pytest.raises(ValueError):
        run(Scenario.model_validate(data), generate(market), type(binding).model_validate(terms))
