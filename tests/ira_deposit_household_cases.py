"""Synthetic one-year variants preserve the matching IRA and tax horizons."""

from wealthlab.household.scenario import Scenario
from wealthlab.retirement.ira_deposit_household_example import synthetic


def one_year():
    data = synthetic().model_dump(mode="json")
    data["end"] = "2027-01-01"
    data["tax_plan"]["cases"] = data["tax_plan"]["cases"][:1]
    plan = data["ira_plan"]
    plan["orders"] = [o for o in plan["orders"] if o["date"].startswith("2026")]
    plan["contributions"]["years"] = plan["contributions"]["years"][:1]
    plan["contributions"]["orders"] = [
        o for o in plan["contributions"]["orders"] if o["date"].startswith("2026")
    ]
    return Scenario.model_validate(data)
