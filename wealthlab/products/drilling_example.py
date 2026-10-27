"""Original synthetic cash-basis drilling cases with independently supplied tax facts."""

from datetime import timedelta

from wealthlab.household.calendar import months
from wealthlab.household.example import synthetic as household
from wealthlab.household.scenario import Scenario
from wealthlab.products.drilling_example_rows import observation
from wealthlab.products.drilling_example_terms import terms
from wealthlab.tax.projection_example import template


def synthetic(profile="base"):
    data = household().model_dump(mode="json")
    data["name"] = "Synthetic conditional drilling: " + profile
    data["accounts"] = [
        dict(
            id="cash",
            provenance="illustration",
            owner="joint",
            currency="USD",
            wrapper="cash",
            balance="200000",
            monthly_fee="0",
        ),
        dict(
            id="drilling",
            provenance="illustration",
            owner="person_a",
            currency="USD",
            wrapper="taxable",
            balance="0",
            monthly_fee="0",
        ),
    ]
    data["members"][0]["retirement_date"] = "2030-01-01"
    data["expenses"][0]["monthly_amount"] = "2000"
    scenario = Scenario.model_validate(data)
    plan = terms()
    plan["observations"] = [
        observation(i, end - timedelta(days=1), profile)
        for i, (_, end) in enumerate(months(scenario.start, scenario.end))
    ]
    data.update(drilling_plan=plan, tax_plan=template(scenario).model_dump(mode="json"))
    return Scenario.model_validate(data)
