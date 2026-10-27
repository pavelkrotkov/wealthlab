"""Independent zero-production year:100k costs and40k exit, versus retaining200k cash."""

from copy import deepcopy
from datetime import date, timedelta

from drilling_cases import short

from wealthlab.household.calendar import months
from wealthlab.household.scenario import Scenario
from wealthlab.optimization.drilling_example import confirm_synthetic, offer
from wealthlab.optimization.inputs import PolicySearch
from wealthlab.products.drilling_market_example import synthetic


def case():
    data = short().model_dump(mode="json")
    data["end"] = "2027-01-01"
    for member in data["members"]:
        member["birth_date"] = "1970-01-01"
    original = data["drilling_plan"]["observations"][0]
    rows = []
    for index, (_, end) in enumerate(months(date(2026, 1, 1), date(2027, 1, 1))):
        row = deepcopy(original)
        row.update(
            id=f"month_{index}", date=str(end - timedelta(days=1)), exit_requested=index == 11
        )
        row["exit_gross_proceeds"] = "40000" if index == 11 else "0"
        if index:
            row.update(
                capital_call="0", idc_cost="0", tangible_cost="0", manager_fee="0", deductions=[]
            )
        rows.append(row)
    plan = data["drilling_plan"]
    plan["observations"] = rows
    starter = synthetic("monte_carlo")
    market = starter.market.model_dump(mode="json")
    market.update(
        end=data["end"], paths=1, expected_annual_inflation=0, annual_inflation_volatility=0
    )
    for asset in market["assets"]:
        asset.update(expected_annual_mark_return=0, annual_volatility=0)
    case = dict(
        household=Scenario.model_validate(data).model_dump(mode="json"),
        binding=starter.binding.model_dump(mode="json"),
        training=market,
        validation=dict(market, seed=market["seed"] + 1),
        drilling_offers=[
            offer("well", plan),
            offer("shares", dict(plan, mode="liquid_reference")),
            offer("no_entry", None),
        ],
        dimensions=[
            dict(
                id="participation",
                choices=[dict(id=k, drilling_offer=k) for k in ("well", "shares", "no_entry")],
            )
        ],
        targets=dict(target_age=50, reserve_years=0, maximum_issuer_weight=None),
    )
    return confirm_synthetic(PolicySearch.model_validate(case).model_dump(mode="json"))


def changed(profile, edit, reconfirm=True):
    data = profile.model_dump(mode="json")
    edit(data)
    if reconfirm:
        data["drilling_envelope"] = None
        return confirm_synthetic(data)
    return PolicySearch.model_validate(data)
