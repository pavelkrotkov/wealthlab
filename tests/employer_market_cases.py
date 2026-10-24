"""A one-year synthetic employer book permits independent cash/value/tax checks."""

from wealthlab.household.scenario import Scenario
from wealthlab.markets.employer_example import synthetic
from wealthlab.markets.inputs import MarketCase
from wealthlab.markets.paths import generate


def flat():
    household, market, binding = synthetic()
    data = household.model_dump(mode="json")
    data.update(end="2027-01-01", expenses=[])
    data["tax_plan"]["cases"] = data["tax_plan"]["cases"][:1]
    data["employment_plan"]["paths"][0]["changes"] = []
    data["compensation_plan"]["events"] = [
        e for e in data["compensation_plan"]["events"] if e["kind"] == "allocation"
    ]
    terms = market.model_dump(mode="json")
    terms.update(end="2027-01-01", expected_annual_inflation=0)
    terms["assets"][0]["expected_annual_mark_return"] = 1.02**12 - 1
    return Scenario.model_validate(data), MarketCase.model_validate(terms), binding


def change(household, **updates):
    return Scenario.model_validate(dict(household.model_dump(mode="json"), **updates))


def crashed():
    household, market, binding = flat()
    data = market.model_dump(mode="json")
    data["assets"][0]["expected_annual_mark_return"] = 0
    data.update(
        mode="stress", shocks=[dict(name="decline", month=0, mark_shocks=dict(employer=-0.5))]
    )
    return household, generate(MarketCase.model_validate(data)), binding
