"""Large supplied US W2 makes the real mixed-credit country limitation bind.

The W2 is already recognized and payroll paid before projection; existing
cash reflects that history. A real700000 stock sale recognizes600000 gain,
with zero pre-move appreciation and independently assumed PR source election.
No historical salary or source receipt is deposited again.
"""

from wealthlab.household.scenario import Scenario
from wealthlab.tax.foreign_credit_example import amount
from wealthlab.tax.pr_execution_positive_gain_example import positive_credit


def binding_mixed():
    data = positive_credit().model_dump(mode="json")
    data["accounts"][0]["balance"] = "2000000"
    annual = data["tax_plan"]["cases"][0]
    annual["federal_income"]["wages_primary"] = "3000000"
    annual["nj_income"]["wages"] = "3000000"
    annual["payments"]["employee_payroll_withheld"] = "79618.20"
    context = annual["pr_federal"]
    wage = dict(
        id="us_prior_service_w2",
        owner_id="person_a",
        classification_assumed_confirmed=True,
        income=dict(
            received="2025-06-30",
            owner="primary",
            kind="wages",
            federal_amount="3000000",
            pr_amount="3000000",
            federal_source="US",
            pr_source="US",
            us_government_wages=False,
            evidence="Supplied synthetic US-source prior-service W2",
        ),
    )
    context["sources"].insert(0, wage)
    profile = context["gain_profile"]
    profile["treatment"] = "ordinary"
    profile["gains"][0]["facts"].update(federal_move_fmv="100000", pr_move_fmv="100000")
    credit = data["foreign_tax_plan"]["credit_profiles"][0]
    credit["annual"] = annual
    credit["income"].insert(
        0,
        dict(
            id="us_prior_service_w2",
            owner_id="person_a",
            country="US",
            kind="wages",
            basket="general",
            value=amount("2025-06-30", 3000000),
            source_classification="Independently supplied synthetic US-source prior service",
        ),
    )
    return Scenario.model_validate(data)
