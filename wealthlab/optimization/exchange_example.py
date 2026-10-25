"""Retain, contribute part/all, or sell the same synthetic source stock directly.

Only source capital is added once when this starter creates a missing book.
Every alternative retains the same actual quantity, basis and opening value.
Zero supplied fund cash/tax/basis flows permit all four synthetic profiles;
nonzero source facts require explicitly entered complete offers instead.
"""

from datetime import timedelta
from decimal import Decimal

from wealthlab.household.scenario import Scenario
from wealthlab.markets.example import asset
from wealthlab.optimization.inputs import PolicySearch
from wealthlab.optimization.product_example import account, add_factor
from wealthlab.optimization.product_example_terms import exchange
from wealthlab.products.exchange_fund_direct import has_fund_facts
from wealthlab.products.exchange_fund_example import request
from wealthlab.products.exchange_fund_inputs import ExchangeFundPlan


def extend(case):
    if not case.household.synthetic:
        raise ValueError("The exchange starter only extends synthetic examples.")
    if case.exchange_opportunities:
        raise ValueError("The exchange starter cannot replace existing contribution offers.")
    data = case.model_dump(mode="json")
    if data["household"]["exchange_fund_plan"] is None:
        add_source(data)
    plan = data["household"]["exchange_fund_plan"]
    if any(has_fund_facts(o) for o in ExchangeFundPlan.model_validate(plan).observations):
        raise ValueError("Enter complete supplied offers for nonzero exchange fund flows.")
    data["exchange_opportunities"] = [
        profile(data, name, fraction)
        for name, fraction in (("retain", 0), ("half", Decimal("0.5")), ("all", 1))
    ]
    data["exchange_opportunities"].append(profile(data, "direct", 1, direct=True))
    data["dimensions"].append(
        dict(
            id="exchange_contribution",
            choices=[
                dict(id=p["id"], exchange_path=p["id"]) for p in data["exchange_opportunities"]
            ],
        )
    )
    return PolicySearch.model_validate(data)


def add_source(data):
    household = data["household"]
    household["accounts"].append(account("exchange", "taxable"))
    household["exchange_fund_plan"] = exchange(Scenario.model_validate(household))
    plan = household["exchange_fund_plan"]
    data["binding"].update(
        exchange_factors={
            key: "exchange_source" if key == plan["source_security"]["id"] else "exchange_basket"
            for key in plan["opening_prices"]
        },
        replace_exchange_observations_confirmed=True,
    )
    for market in [
        data["training"],
        data["validation"],
        *(c["market"] for c in data["robustness"].values()),
    ]:
        add_factor(market, asset("exchange_source", "equity", 0.04, 0.3, 0))
        add_factor(market, asset("exchange_basket", "equity", 0.04, 0.18, 0))


def profile(data, identity, fraction, direct=False):
    household = data["household"]
    plan = ExchangeFundPlan.model_validate(household["exchange_fund_plan"]).model_dump(mode="json")
    plan["mode"] = "direct_sale" if direct else "exchange"
    plan["contribution_quantity"] = str(Decimal(plan["source_lot"]["quantity"]) * fraction)
    end = Scenario.model_validate(household).end
    plan["requests"].append(
        request("optimizer_source_exit", end - timedelta(days=1), "sell_source")
    )
    plan["requests"].sort(key=lambda item: str(item["date"]))
    return dict(
        id=identity,
        provenance="illustration",
        plan=plan,
        source="Original synthetic whole-source profiles; zero fund flows, no sponsor terms",
        available_on=household["start"],
        complete_cash_tax_and_basis_profile_confirmed=True,
        profile_valid_for_projected_income_and_market_paths_confirmed=True,
    )
