"""Compare cash with fixed product opportunities using the same original household capital.

The supplied zero allocation schedules are illustrative conditional assumptions,
not predicted tax losses. Each10000unit requires its own cash purchase and uses
the same fixed rates, dates and contract on every selected number of units.
"""

from wealthlab.optimization.inputs import PolicySearch
from wealthlab.optimization.product_example_terms import sleeve


def extend(case):
    if not case.household.synthetic:
        raise ValueError("The allocation starter only extends synthetic examples.")
    data = case.model_dump(mode="json")
    data["sleeve_opportunities"] = [opportunity(case, private) for private in (False, True)]
    data["dimensions"].append(
        dict(
            id="opening_product_mix",
            choices=[
                dict(id=name, sleeve_units=dict(new_margin=margin, new_private=fund))
                for name, margin, fund in (
                    ("cash", 0, 0),
                    ("margin", 2, 0),
                    ("private_fund", 0, 2),
                    ("blend", 1, 1),
                )
            ],
        )
    )
    return PolicySearch.model_validate(data)


def opportunity(case, private):
    identity = "new_private" if private else "new_margin"
    unit = sleeve(case.household, case.training.assets[0].id, private)
    unit = namespaced(unit, identity)
    unit["account_id"] = identity
    if unit["private_fund_contract"] is not None:
        unit["private_fund_contract"]["ordinary_holding_period_assumed_confirmed"] = True
    return dict(
        id=identity,
        provenance="illustration",
        cash_account="cash",
        owner="person_a",
        unit=unit,
        minimum_units=0,
        maximum_units=5,
        opening_cash_purchase_assumed_confirmed=True,
        proportional_dollar_schedules_assumed_confirmed=True,
        replace_observations_with_shared_paths_confirmed=True,
    )


def namespaced(value, prefix):
    if isinstance(value, list):
        return [namespaced(item, prefix) for item in value]
    if not isinstance(value, dict):
        return value
    return {
        key: prefix + "_" + item if key == "id" else namespaced(item, prefix)
        for key, item in value.items()
    }
