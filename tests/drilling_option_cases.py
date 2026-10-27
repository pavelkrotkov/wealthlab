"""Original shared-wallet case: an actual option premium completes a drilling capital call."""

from wealthlab.household.scenario import Scenario
from wealthlab.products.drilling_example import synthetic as drilling
from wealthlab.products.option_household_example import synthetic as options


def blended():
    data = options().model_dump(mode="json")
    data["accounts"][0]["balance"] = "99500"
    data["expenses"] = []
    source = drilling().model_dump(mode="json")
    data["accounts"].append(source["accounts"][1])
    data["drilling_plan"] = source["drilling_plan"]
    data["drilling_plan"]["observations"] = [
        row for row in source["drilling_plan"]["observations"] if row["date"] < data["end"]
    ]
    return Scenario.model_validate(data)


def conflict(kind):
    data = blended().model_dump(mode="json")
    if kind == "account":
        data["drilling_plan"]["account_id"] = "options"
    else:
        data["option_plan"]["case"]["holdings"]["securities"][0]["wash_group"] = (
            "drilling_reference_security"
        )
    return Scenario.model_validate(data)
