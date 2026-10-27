"""Actual PR-service salary and pre-move stock gains share native cash and paid-credit limits."""

from wealthlab.household.scenario import Scenario
from wealthlab.tax.pr_execution_positive_gain_example import positive_credit
from wealthlab.tax.pr_execution_salary_example import monthly


def mixed_credit():
    data = positive_credit().model_dump(mode="json")
    salary = monthly().model_dump(mode="json")
    data.update(name="Synthetic PR-service W2 and actual pre-move stock-credit execution")
    data["incomes"] = salary["incomes"]
    annual = data["tax_plan"]["cases"][0]
    earlier = salary["tax_plan"]["cases"][0]
    annual["federal_income"]["wages_primary"] = "80000"
    annual["nj_income"]["wages"] = "80000"
    annual["payments"]["employee_payroll_withheld"] = "6120"
    context = annual["pr_federal"]
    wages = earlier["pr_federal"]["sources"]
    for row in wages:
        row["income"].update(federal_source="PR", pr_source="PR")
    context["sources"] = wages + context["sources"]
    data["tax_plan"]["income_rules"] = salary["tax_plan"]["income_rules"]
    profile = data["foreign_tax_plan"]["credit_profiles"][0]
    profile["annual"] = annual
    credits = salary["foreign_tax_plan"]["credit_profiles"][0]["income"]
    for row in credits:
        row["country"] = "PR"
    profile["income"] = credits + profile["income"]
    return Scenario.model_validate(data)
