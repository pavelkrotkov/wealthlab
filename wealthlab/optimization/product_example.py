"""Add fixed synthetic products; every policy shares their capital and contract assumptions.

Each product adds10000 of synthetic opening wealth, not a free purchase funded
by the existing cash account. Allocations and tax assumptions are illustrative
inputs, not claims about a sponsor, a tax benefit or an insurer return.
"""

from wealthlab.household.scenario import Scenario
from wealthlab.optimization.inputs import PolicySearch
from wealthlab.optimization.product_example_terms import exchange, insurance, sleeve


def extend(case):
    if not case.household.synthetic:
        raise ValueError("The product starter only extends synthetic examples.")
    data = case.model_dump(mode="json")
    household = data["household"]
    scenario = Scenario.model_validate(household)
    household["accounts"] += [
        account(identity, wrapper)
        for identity, wrapper in (
            ("margin_sleeve", "taxable"),
            ("private_fund", "taxable"),
            ("exchange", "taxable"),
            ("life_policy", "insurance"),
        )
    ]
    factor = data["training"]["assets"][0]["id"]
    household["sleeve_plan"] = dict(
        sleeves=[sleeve(scenario, factor, False), sleeve(scenario, factor, True)],
        other_tax_inputs_exclude_supplied_allocations_confirmed=True,
        actual_household_cash_confirmed=True,
        priority="after_prior_tax_arrears_before_wrapper_deposits_and_current_tax",
    )
    household["exchange_fund_plan"] = exchange(scenario)
    household["life_plan"] = insurance(scenario)
    data["binding"].update(
        sleeves=["margin_sleeve", "private_fund"],
        replace_sleeve_observations_confirmed=True,
        exchange_factors={
            key: "exchange_prices" for key in household["exchange_fund_plan"]["opening_prices"]
        },
        replace_exchange_observations_confirmed=True,
    )
    markets = [data["training"], data["validation"]]
    markets.extend(check["market"] for check in data["robustness"].values())
    for market in markets:
        add_factor(market)
    return PolicySearch.model_validate(data)


def account(identity, wrapper):
    return dict(
        id=identity,
        owner="person_a",
        provenance="illustration",
        currency="USD",
        wrapper=wrapper,
        balance="10000",
        monthly_fee="0",
    )


def add_factor(market, factor=None):
    market["assets"].append(
        factor
        or dict(
            id="exchange_prices",
            provenance="illustration",
            role="equity",
            expected_annual_mark_return=0.04,
            annual_volatility=0.18,
            annual_cash_yield=0,
        )
    )
    original = market["correlation"]
    # Insert an independent price factor before the existing final inflation axis.
    market["correlation"] = [[*row[:-1], 0, row[-1]] for row in original[:-1]]
    market["correlation"] += [[0] * (len(original) - 1) + [1, 0]]
    market["correlation"] += [[*original[-1][:-1], 0, original[-1][-1]]]
    identity = market["assets"][-1]["id"]
    if market["historical"] is not None:
        history = market["historical"]
        history["source"] += f"; added synthetic zero-return {identity} price proxy"
        for month in history["months"]:
            month["mark_returns"][identity] = month["cash_yields"][identity] = 0
