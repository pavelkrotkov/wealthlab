"""A one-year proxy has exactly 1% mark return plus 1% cash yield each month."""

from wealthlab.household.scenario import Scenario
from wealthlab.markets.inputs import MarketCase
from wealthlab.markets.wrapper_example import synthetic


def flat():
    scenario, market, binding = synthetic()
    data = scenario.model_dump(mode="json")
    data.update(end="2027-01-01", expenses=[])
    data["tax_plan"]["cases"] = data["tax_plan"]["cases"][:1]
    data["ira_plan"].update(
        orders=[],
        returns=[
            dict(
                id="entered_forecast",
                provenance="illustration",
                date="2026-06-01",
                account_id="retirement",
                rate=".5",
            )
        ],
    )
    data["education_plan"].update(contributions=[], tuition=[], returns=[])
    paths = market.model_dump(mode="json")
    paths.update(end=data["end"], expected_annual_inflation=0)
    paths["assets"][0].update(expected_annual_mark_return=1.01**12 - 1, annual_cash_yield=0.12)
    return Scenario.model_validate(data), MarketCase.model_validate(paths), binding


def lock(paths):
    data = paths.model_dump(mode="json")
    data.update(
        mode="stress",
        shocks=[dict(name="outgoing wrapper restriction", month=0, lock_months=dict(portfolio=12))],
    )
    return MarketCase.model_validate(data)
