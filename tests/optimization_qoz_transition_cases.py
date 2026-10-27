"""A complete original monthly source-sale profile closes2026 before investing in2027.

Zero returns/fees isolate actual prior-year taxes, dated refunds and two-year
NJ bracket use. All future years explicitly reuse the2025tax-rule assumption.
"""

from copy import deepcopy

from qoz_transition_cases import transition

from wealthlab.household.scenario import Scenario
from wealthlab.markets.qoz_example import binding, market_case
from wealthlab.optimization.inputs import PolicySearch
from wealthlab.optimization.qoz_example import offers


def case():
    data = transition().model_dump(mode="json")
    original = data["lot_plan"]["case"]["trades"].pop()
    data["lot_plan"]["case"]["sale_policies"] = [
        dict(
            id=original["id"],
            provenance="illustration",
            date="2026-12-31",
            account_id=original["account_id"],
            security_id=original["security_id"],
            mode="sell_all",
            prices=data["lot_plan"]["opening_prices"],
            commission="0",
            selection="hifo",
        )
    ]
    for row in data["qoz_plan"]["observations"]:
        row["locked"] = False
    household = Scenario.model_validate(data)
    market = market_case(household, "monte_carlo", "early_crash").model_dump(mode="json")
    market.update(paths=1, expected_annual_inflation=0, annual_inflation_volatility=0)
    for asset in market["assets"]:
        asset.update(expected_annual_mark_return=0, annual_volatility=0, annual_cash_yield=0)
    profiles = offers(deepcopy(data["qoz_plan"]), household.start)
    return PolicySearch.model_validate(
        dict(
            household=household,
            binding=binding(),
            training=market,
            validation=dict(market, seed=market["seed"] + 1),
            qoz_offers=profiles,
            dimensions=[
                dict(
                    id="qoz_participation",
                    choices=[dict(id=o["id"], qoz_offer=o["id"]) for o in profiles],
                )
            ],
            targets=dict(target_age=50, reserve_years=0, maximum_issuer_weight=None),
        )
    )
