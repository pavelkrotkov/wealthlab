"""The native new-regime small-gain oracle is now an actual completed household sale."""

from wealthlab.household.scenario import Scenario
from wealthlab.tax.pr_execution_positive_gain_example import positive_credit


def small_gain():
    data = positive_credit().model_dump(mode="json")
    data.update(start="2029-09-01", end="2030-01-01")
    annual = data["tax_plan"]["cases"][0]
    annual["policy"].update(year=2029, mode="freeze_2025")
    annual.update(nj_regime="freeze_2025")
    annual["filing"]["age_primary"] = 44
    context = annual["pr_federal"]
    context.update(pr_regime="freeze_2025")
    context["primary"].update(local_start="2027-01-01", local_end="2029-12-31")
    context["sources"][0]["income"].update(
        received="2029-10-31", federal_amount="1000", pr_amount="1000"
    )
    profile = context["gain_profile"]
    profile["decree"].update(
        application_date="2027-01-01",
        granted_on="2027-02-01",
        effective_from="2027-01-01",
        residence_since="2027-01-01",
        six_prior_years_nonresident="assumed",
    )
    profile["gains"][0]["facts"].update(
        acquired="2027-03-01",
        sale_proceeds="101000",
        federal_possession_start="2027-01-01",
        pr_resident_since="2027-01-01",
        federal_move_fmv="0",
        pr_move_fmv="0",
    )
    foreign = data["foreign_tax_plan"]
    foreign["assessments"][0].update(liability_year=2029, observed="2029-12-31")
    foreign["schedules"][0].update(
        source_income_year=2029, due_date="2029-12-31", requested_native="1000"
    )
    foreign["credit_profiles"][0].update(annual=annual, as_of="2029-12-31")
    foreign["credit_profiles"][0]["income"][0]["value"].update(date="2029-10-31", amount="1000")
    for quote in foreign["quotes"]:
        quote["date"] = "2029" + quote["date"][4:]
    data["accounts"][1]["balance"] = "101000"
    for expense in data["expenses"]:
        expense.update(start="2029-12-01", end="2030-01-01")
    native = data["lot_plan"]["case"]
    native.update(as_of=data["start"], end="2029-12-31")
    native["lots"][0].update(
        acquired="2027-03-01",
        federal_holding_start="2027-03-01",
        liquid_after="2027-03-01",
        quantity="1010",
        nj_basis="100000",
    )
    native["trades"][0].update(date="2029-10-31", quantity="1010")
    for mark in data["lot_plan"]["monthly_marks"]:
        mark["date"] = "2029" + mark["date"][4:]
    return Scenario.model_validate(data)
