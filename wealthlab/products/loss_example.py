"""Illustrate supplied losses independently of market returns and provider claims."""

from wealthlab.household.scenario import Scenario


def enable(scenario, federal, new_jersey):
    data = scenario.model_dump(mode="json")
    for sleeve in data["sleeve_plan"]["sleeves"]:
        for allocation in sleeve["allocations"]:
            allocation["federal"]["long_term"] = "-12000"
            allocation["new_jersey"]["business"]["partnership"] = "-12000"
            year = int(allocation["date"][:4])
            for jurisdiction, treatment in (("federal", federal), ("new_jersey", new_jersey)):
                allocation[f"{jurisdiction}_loss"] = dict(
                    treatment=treatment,
                    release_on=f"{year + 1}-12-01" if treatment == "deferred" else None,
                    eligibility_after_limits_assumed=True,
                )
    return Scenario.model_validate(data)
