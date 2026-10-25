"""Short household cases retain complete annual wage assessments and actual tax settlement."""

from wealthlab.household.scenario import Scenario
from wealthlab.retirement.social_work_household_example import synthetic
from wealthlab.tax.projection_example import template


def payload():
    raw = synthetic().model_dump(mode="json")
    raw["end"] = "2028-01-01"
    raw["social_security"]["end_year"] = 2028
    raw["social_work_plan"]["years"] = raw["social_work_plan"]["years"][:2]
    raw["expenses"][0]["end"] = "2028-01-01"
    raw["tax_plan"]["cases"] = raw["tax_plan"]["cases"][:2]
    return raw


def case():
    return Scenario.model_validate(payload())


def completed(rows, year):
    return next(r["annual_tax"] for r in rows if r["date"] == f"{year}-12-01")


def replan(raw):
    scenario = Scenario.model_validate(raw)
    return scenario.model_copy(update=dict(tax_plan=template(scenario)))
