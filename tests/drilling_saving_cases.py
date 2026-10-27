"""Optional liquid saving shares actual post-product cash, not the drilling capital budget."""

from drilling_cases import short

from wealthlab.household.scenario import Scenario
from wealthlab.portfolio.saving_example import synthetic as saving


def blended():
    data = saving().model_dump(mode="json")
    data["accounts"][0]["balance"] = "100000"
    data["expenses"] = []
    source = short(3).model_dump(mode="json")
    data["accounts"].append(source["accounts"][1])
    data["drilling_plan"] = source["drilling_plan"]
    return Scenario.model_validate(data)
