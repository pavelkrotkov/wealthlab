"""Fixed original home and lien assumptions accompany existing retirement policies.

Only synthetic factories enter here. Imported property observations, costs,
recognition and sale decisions remain user supplied and are never regenerated.
"""

from wealthlab.household.property_example import plan
from wealthlab.household.property_example import synthetic as home
from wealthlab.household.scenario import Scenario
from wealthlab.optimization.inputs import PolicySearch


def extend(case):
    if not case.household.synthetic or case.household.property_plan is not None:
        raise ValueError(
            "The fixed-home starter requires a synthetic case without a property plan."
        )
    data = case.model_dump(mode="json")
    original = home()
    household = data["household"]
    household["name"] += "; fixed sourced home and native lien close"
    household["accounts"].extend(
        a.model_dump(mode="json") for a in original.accounts if a.wrapper == "property"
    )
    household["debts"].extend(d.model_dump(mode="json") for d in original.debts)
    household["property_plan"] = plan(Scenario.model_validate(household))
    # Native home marks retain unmeasured issuer coverage; this example explicitly
    # disables that optional limit rather than inventing an issuer/factor proxy.
    data["targets"]["maximum_issuer_weight"] = None
    return PolicySearch.model_validate(data)
