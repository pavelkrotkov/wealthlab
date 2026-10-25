"""Only complete conditional policy paths may contribute to household funding conclusions.

Qualification and source completeness are user-supplied facts, not conclusions
inferred from an account label. A fully funded standalone replay validates the
planned tax path; the live household separately executes failed-payment exits.
"""

from wealthlab.products.life_contract import run
from wealthlab.products.life_contract_inputs import LifeContractCase
from wealthlab.products.life_contract_tax import known
from wealthlab.products.life_household_accounts import validate_account
from wealthlab.products.life_household_calendar import required_values, reserve_end
from wealthlab.products.life_household_records import validate_events, validate_values


def validate(scenario):
    plan = scenario.life_plan
    if scenario.tax_plan is None:
        raise ValueError("Household life policies require a shared annual tax plan.")
    ids = [h.account_id for h in plan.holdings]
    if len(set(ids)) != len(ids):
        raise ValueError("Each life-policy account must have one owning ledger.")
    members = {m.id: m for m in scenario.members}
    if set(plan.insurance_need_by_owner) - set(members):
        raise ValueError("Insurance needs must refer to known household members.")
    for holding in plan.holdings:
        validate_account(scenario, holding, members)
        validate_path(scenario, holding)


def validate_path(scenario, holding):
    contract = holding.contract
    if not known(contract) or not holding.other_inputs_exclude_policy_confirmed:
        raise ValueError("Confirm policy eligibility and remove duplicated cash/tax inputs.")
    if not contract.values_match_executed_events_confirmed:
        raise ValueError("Confirm policy values correspond to the selected executed path.")
    if contract.start != scenario.start or holding.opening_values.date != scenario.start:
        raise ValueError("Policy opening snapshot must match the household start date.")
    validate_calendar(scenario, holding)
    validate_events(scenario, holding)
    validate_recognition(holding)


def validate_calendar(scenario, holding):
    if holding.payments_complete_through < reserve_end(scenario.end, scenario.reserve_years):
        raise ValueError(
            "Complete the policy payment schedule through the household reserve horizon."
        )
    values = {v.date: v for v in holding.contract.values}
    if required_values(scenario, holding.contract) - set(values):
        raise ValueError("Supply a post-event policy value for every in-force month end.")
    for value in values.values():
        validate_values(value)


def validate_recognition(holding):
    result = run(
        LifeContractCase(
            synthetic=True,
            contract=holding.contract,
            insurance_need=None,
            retirement_date=None,
        )
    )
    if any(row["unknown_fields"] for row in result["annual"]):
        raise ValueError("Household policy tax recognition must be explicit in both jurisdictions.")
