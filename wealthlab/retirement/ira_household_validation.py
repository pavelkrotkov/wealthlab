"""Block ambiguous IRA pools and duplicate recognition before fixed schedules move cash.

This bridge covers complete calendar years, ordinary USD IRAs and year-end
settlement. Contributions, workplace/inherited holdings and tax withholding
from the IRA need their own supported adapters rather than inferred treatment.
"""

from types import SimpleNamespace

from wealthlab.retirement.account_liquidity import validate as validate_liquidity
from wealthlab.retirement.distribution_owner_validation import validate_tax_ages
from wealthlab.tax.projection_validation import validate as validate_tax


def validate(scenario):
    plan = scenario.ira_plan
    if scenario.tax_plan is None:
        raise ValueError("Household IRA schedules require an explicit tax plan.")
    validate_tax(scenario.tax_plan, scenario)
    if not (
        plan.complete_ordinary_ira_pools_confirmed
        and plan.other_tax_inputs_exclude_ira_events_confirmed
    ):
        raise ValueError("Confirm complete ordinary IRA pools and no duplicated IRA tax inputs.")
    if (scenario.start.month, scenario.start.day, scenario.end.month, scenario.end.day) != (
        1,
        1,
        1,
        1,
    ):
        raise ValueError("Household IRA schedules currently require complete calendar years.")
    if scenario.tax_plan.settlement_timing != "year_end":
        raise ValueError(
            "Annual IRA basis reconciliation requires year-end settlement in this bridge."
        )
    validate_people(scenario)
    validate_records(scenario)
    validate_sources(scenario)


def validate_people(scenario):
    plan = scenario.ira_plan
    members = [(p.id, p.birth_date) for p in scenario.members]
    if [(p.id, p.birth_date) for p in plan.owners] != members:
        raise ValueError("IRA owners must match household members and birth dates in filing order.")
    for annual in scenario.tax_plan.cases:
        context = SimpleNamespace(year=annual.policy.year, owners=plan.owners)
        validate_tax_ages(context, annual.filing, True)
        validate_tax_ages(context, annual.nj_filing or annual.filing, False)


def validate_records(scenario):
    plan = scenario.ira_plan
    records = [*plan.owners, *plan.orders, *plan.returns, *plan.liquidity_locks]
    validate_liquidity(plan.liquidity_locks, plan.products, scenario.start, scenario.end)
    ids = [r.id for r in records]
    if len(ids) != len(set(ids)) or any(r.provenance == "unresolved" for r in records):
        raise ValueError("IRA plan records need unique IDs and resolved assumptions.")
    if any(not scenario.start <= e.date < scenario.end for e in [*plan.orders, *plan.returns]):
        raise ValueError("IRA events must lie inside the household projection.")


def validate_sources(scenario):
    plan = scenario.ira_plan
    accounts = {a.id for a in scenario.accounts if a.wrapper in {"traditional", "roth"}}
    workplace = set(scenario.workplace_plan.products) if scenario.workplace_plan else set()
    accounts -= workplace
    if not accounts or accounts != set(plan.products):
        raise ValueError(
            "Explicitly classify every household traditional/Roth account as an ordinary IRA."
        )
    if any(c.destination in accounts for c in scenario.contributions):
        raise ValueError("IRA household contributions require the contribution integration layer.")
    validate_tax_inputs(scenario)


def validate_tax_inputs(scenario):
    if any(r.federal == "ira_distributions" for r in scenario.tax_plan.income_rules):
        raise ValueError("Remove manual IRA income rules when using IRA schedules.")
    inputs = [c.federal_income for c in scenario.tax_plan.cases]
    inputs += [e.federal for e in scenario.tax_plan.events]
    if any(
        any((i.ira_distributions, i.retirement_additional_tax, i.deductible_ira_contributions))
        for i in inputs
    ):
        raise ValueError(
            "Remove manual IRA income/additional-tax/deduction amounts when using IRA schedules."
        )
