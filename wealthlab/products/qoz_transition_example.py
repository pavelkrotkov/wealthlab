"""Actual December 2026 source sale funds a timely January 2027 new-regime call."""

from wealthlab.household.scenario import Scenario
from wealthlab.products.qoz_example import contract, economic_case, source_plan
from wealthlab.products.qoz_example import synthetic as same_year
from wealthlab.tax.projection_example import template


def synthetic():
    data = same_year(2027).model_dump(mode="json")
    data.update(name="Synthetic QOZ prior-year source-return revision", start="2026-01-01")
    scenario = Scenario.model_validate(data)
    linked = source_plan(scenario, 2026)
    linked["case"]["trades"][0]["date"] = "2026-12-15"
    plan = contract(scenario, economic_case(), 2027)
    plan["prior_source_year_revision_assumed_confirmed"] = True
    data.update(lot_plan=linked, qoz_plan=plan, tax_plan=template(scenario).model_dump(mode="json"))
    return Scenario.model_validate(data)
