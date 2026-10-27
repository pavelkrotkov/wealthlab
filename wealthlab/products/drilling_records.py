"""Complete source records keep expense, basis and tax assumptions explicit and reproducible.

Legal form does not determine SE earnings or permitted loss use. Supplemental
SE/QBI/AMT inputs remain separate from actual cash-basis ordinary income, and
unsupported retirement earnings combinations must be rejected before cash runs.
"""

from wealthlab.products.conditional_allocations import event
from wealthlab.products.drilling_cash import COSTS
from wealthlab.tax.nj_facts import NJIncome
from wealthlab.tax.projection_validation import validate_event

SPECIAL = {
    "partnership_se_earnings_primary",
    "partnership_se_earnings_spouse",
    "partnership_qbi_before_se_deduction",
    "partnership_qbi_w2_wages",
    "partnership_qbi_qualified_property",
    "additional_amt_income",
}


def validate_records(plan):
    records = [*plan.observations, *(d for o in plan.observations for d in o.deductions)]
    if len({r.id for r in records}) != len(records):
        raise ValueError("Drilling observation/deduction IDs must be unique.")
    if any(r.provenance == "unresolved" for r in records):
        raise ValueError("Resolve drilling illustration provenance before calculation.")
    for observation in plan.observations:
        validate_observation(observation)


def validate_observation(observation):
    if len({d.component for d in observation.deductions}) != len(observation.deductions):
        raise ValueError("Each drilling deduction component appears once per month.")
    if any(getattr(observation, k) for k in COSTS[:3]) and not any(
        d.component == "operating_loss" for d in observation.deductions
    ):
        raise ValueError("Supply operating-loss basis/limit facts for cash operating expenses.")


def validate_tax(scenario, plan):
    for observation in plan.observations:
        validate_supplements(observation)
        validate_earnings(scenario, plan, observation)


def validate_supplements(observation):
    fields = observation.supplemental_federal.model_dump()
    if any(value for key, value in fields.items() if key not in SPECIAL):
        raise ValueError("Drilling supplements only independently supplied SE/QBI/AMT facts.")
    validate_event(
        event(
            observation.date,
            "Supplied drilling facts",
            observation.supplemental_federal,
            NJIncome(),
        )
    )


def validate_earnings(scenario, plan, observation):
    income = observation.supplemental_federal
    earnings = (income.partnership_se_earnings_primary, income.partnership_se_earnings_spouse)
    if plan.se_classification == "zero_under_supplied_classification" and any(earnings):
        raise ValueError("Zero-SE classification contradicts supplied box14 earnings.")
    if any(earnings) and any((scenario.social_security, scenario.ira_plan)):
        raise ValueError("Generated drilling SE with SSA/IRA needs another earned-income adapter.")
