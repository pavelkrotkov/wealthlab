"""One shared synthetic life/QOZ contract; no private policy or household facts."""

from calendar import monthrange
from datetime import date

from qoz_cases import flat

from wealthlab.household.scenario import Scenario
from wealthlab.products.life_household_calendar import reserve_end
from wealthlab.products.life_household_example import synthetic as life_example


def synthetic():
    case = flat(2026)
    data, other = case.model_dump(mode="json"), life_example().model_dump(mode="json")
    data["accounts"].append(other["accounts"][-1])
    data["life_plan"] = other["life_plan"]
    holding = data["life_plan"]["holdings"][0]
    values = holding["contract"]["values"]
    last = dict(values[-1])
    values.extend(
        dict(last, date=date(2026, month, monthrange(2026, month)[1]).isoformat())
        for month in range(4, 13)
    )
    holding["payments_complete_through"] = reserve_end(case.end, case.reserve_years).isoformat()
    return Scenario.model_validate(data)
