"""Public synthetic ordinary PR and Spain cases, with explicit conditional tax policies."""

from wealthlab.household.scenario import Scenario
from wealthlab.tax.jurisdiction_execution_facts import JurisdictionExecutionCase
from wealthlab.tax.pr_execution_example import household
from wealthlab.tax.spain_execution_example import single


def native_pr():
    data = household(government=True).model_dump(mode="json")
    data["name"] = "Synthetic computed PR assessment and actual shared household cash"
    plan = data["foreign_tax_plan"]
    plan["assessments"][0]["observed"] = "2025-12-31"
    plan["schedules"][0].update(due_date="2025-12-31", requested_native="50000")
    return Scenario.model_validate(data)


def synthetic(country="Puerto Rico"):
    if country == "PR stock gains":
        from wealthlab.tax.pr_execution_gain_example import synthetic_gain

        return JurisdictionExecutionCase(scenario=synthetic_gain())
    if country == "PR W2 and stock credit":
        from wealthlab.tax.pr_execution_mixed_gain_example import mixed_credit

        return JurisdictionExecutionCase(scenario=mixed_credit())
    if country == "PR pre-move credit":
        from wealthlab.tax.pr_execution_positive_gain_example import positive_credit

        return JurisdictionExecutionCase(scenario=positive_credit())
    if country == "Spain":
        scenario, spain = single()
        return JurisdictionExecutionCase(scenario=scenario, spain=spain)
    return JurisdictionExecutionCase(scenario=native_pr())
