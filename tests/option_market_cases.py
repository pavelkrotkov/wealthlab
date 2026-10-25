"""Original flat-path fixtures preserve independent exact cash expectations."""

from wealthlab.household.scenario import Scenario
from wealthlab.markets.inputs import MarketCase
from wealthlab.markets.option_example import synthetic
from wealthlab.markets.paths import generate


def flat(strategy="Four-leg synthetic exposure"):
    scenario, market, binding = synthetic(strategy=strategy)
    data = market.model_dump(mode="json")
    for asset in data["assets"]:
        asset["expected_annual_mark_return"] = 0
    return scenario, generate(MarketCase.model_validate(data)), binding


def change(scenario, update):
    data = scenario.model_dump(mode="json")
    update(data)
    return Scenario.model_validate(data)
