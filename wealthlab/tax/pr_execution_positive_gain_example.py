"""Actual cash executes the native same-basis pre-move gain and positive PR credit oracle."""

from wealthlab.household.scenario import Scenario
from wealthlab.tax.pr_execution_gain_example import synthetic_gain


def positive_credit():
    data = synthetic_gain().model_dump(mode="json")
    data.update(
        name="Synthetic actual pre-move stock gain and positive PR paid-US credit", incomes=[]
    )
    annual = data["tax_plan"]["cases"][0]
    annual["federal_income"]["wages_primary"] = "0"
    annual["nj_income"]["wages"] = "0"
    annual["payments"]["employee_payroll_withheld"] = "0"
    context = annual["pr_federal"]
    context["primary"].update(local_start="2020-01-01", presence_days=365)
    row = context["sources"][-1]
    row["income"].update(federal_amount="600000", pr_amount="600000")
    context["sources"] = [row]
    profile = context["gain_profile"]
    profile["local_us_credit_treatment"] = "allowed"
    profile["decree"].update(
        application_date="2020-01-01",
        granted_on="2020-02-01",
        effective_from="2020-01-01",
        residence_since="2020-01-01",
    )
    profile["gains"][0]["facts"].update(
        acquired="2010-01-01",
        sale_proceeds="700000",
        federal_cost="100000",
        pr_cost="100000",
        federal_move_fmv="200000",
        pr_move_fmv="200000",
        federal_possession_start="2020-01-01",
        pr_resident_since="2020-01-01",
    )
    data["tax_plan"]["income_rules"] = []
    foreign = data["foreign_tax_plan"]
    credit = foreign["credit_profiles"][0]
    credit.update(annual=annual, income=[dict(credit["income"][-1])])
    credit["income"][0]["value"]["amount"] = "600000"
    foreign["schedules"][0].update(requested_native="600000", income_ids=["stock_gain"])
    data["accounts"][1]["balance"] = "700000"
    native = data["lot_plan"]["case"]
    native["lots"][0].update(
        acquired="2010-01-01",
        federal_holding_start="2010-01-01",
        liquid_after="2010-01-01",
        quantity="7000",
        federal_basis="100000",
        nj_basis="150000",
    )
    native["trades"][0]["quantity"] = "7000"
    return Scenario.model_validate(data)
