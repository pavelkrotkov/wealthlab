"""Validate every offered unit profile, including locked and zero-unit alternatives.

Validation assembles one-unit books only to check native contracts and ownership;
that temporary object is never projected or treated as available household capital.
Actual candidate compilation debits source cash and revalidates scaled books.
"""

from wealthlab.household.scenario import Scenario
from wealthlab.optimization.sleeve_allocations import account, add_sleeve
from wealthlab.products.household_validation import validate as validate_sleeves


def validate(case):
    opportunities = case.sleeve_opportunities
    validate_identifiers(opportunities)
    validate_choices(case)
    if not opportunities:
        return
    if case.binding.sleeves and not case.binding.replace_sleeve_observations_confirmed:
        raise ValueError("Confirm replacement of the original sleeve observations independently.")
    data = case.household.model_dump(mode="json")
    used = {a["id"] for a in data["accounts"]}
    for item in opportunities:
        validate_item(item, case)
        if item.unit.account_id in used:
            raise ValueError("An opening sleeve purchase requires a new distinct account.")
        used.add(item.unit.account_id)
        data["accounts"].append(account(item, item.unit.case.opening_equity))
        add_sleeve(data, item.unit.model_dump(mode="json"))
    validate_sleeves(Scenario.model_validate(data))


def validate_item(item, case):
    if item.provenance == "unresolved" or not (
        item.opening_cash_purchase_assumed_confirmed
        and item.proportional_dollar_schedules_assumed_confirmed
        and item.replace_observations_with_shared_paths_confirmed
    ):
        raise ValueError(
            "Confirm opening cash purchase and proportional dollar schedule assumptions."
        )
    validate_purchase_basis(item.unit, case.household.start)
    validate_source(item, case)


def validate_source(item, case):
    accounts = {a.id: a for a in case.household.accounts}
    source = accounts.get(item.cash_account)
    if source is None or (source.wrapper, source.currency) != ("cash", "USD"):
        raise ValueError("Opening sleeve purchases require an existing USD cash account.")
    if {item.unit.case.long_factor, item.unit.case.short_factor} - {
        a.id for a in case.training.assets
    }:
        raise ValueError("Sleeve opportunities must use the shared market factors.")


def validate_choices(case):
    offered = {item.id: item for item in case.sleeve_opportunities}
    for dimension in case.dimensions:
        for choice in dimension.choices:
            validate_units(choice, offered)


def validate_units(choice, offered):
    for identity, count in (choice.sleeve_units or {}).items():
        item = offered.get(identity)
        if item is None or not item.minimum_units <= count <= item.maximum_units:
            raise ValueError("Every sleeve choice must name an offered product within bounds.")


def control_keys(choice):
    return {"sleeve_units:" + key for key in choice.sleeve_units or {}}


def validate_purchase_basis(unit, start):
    contract = unit.private_fund_contract
    if contract is not None and contract.federal_holding_start not in (None, start):
        raise ValueError("A new cash fund cannot inherit a different historical holding start.")
    if contract is not None and not contract.ordinary_holding_period_assumed_confirmed:
        raise ValueError("New cash fund units require confirmed ordinary holding-period treatment.")
    if contract is not None and (
        contract.federal_opening_basis != unit.case.opening_equity
        or contract.new_jersey_opening_basis != unit.case.opening_equity
    ):
        raise ValueError(
            "A new cash-only fund purchase requires supplied unit bases equal to cost."
        )


def validate_identifiers(opportunities):
    if len({item.id for item in opportunities}) != len(opportunities):
        raise ValueError("Sleeve opportunity identifiers must be unique.")
