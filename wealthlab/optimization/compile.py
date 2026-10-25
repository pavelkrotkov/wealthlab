"""Only named policy fields change; capital, spending, tax facts and contract terms stay shared.

Each candidate starts from a fresh serialized baseline and is fully validated
again. Lists replace whole schedules atomically, so clearing harvesting cannot
leave stale trades from an earlier candidate. Funding choices reorder existing
permissions without changing their fees, basis, security or sale selection."""

from wealthlab.household.scenario import Scenario
from wealthlab.markets.household_inputs import HouseholdBinding
from wealthlab.optimization import (
    drilling_controls,
    exchange_paths,
    life_paths,
    new_life_controls,
    new_life_offers,
    option_allocations,
    qoz_controls,
)
from wealthlab.optimization.account_controls import apply as account_changes
from wealthlab.optimization.allocation_validation import validate as validate_allocations
from wealthlab.optimization.option_offer_validation import validate as validate_options
from wealthlab.optimization.scope import validate
from wealthlab.optimization.sleeve_allocations import apply as allocate
from wealthlab.optimization.sleeve_allocations import selections


def compile_candidate(case, selection):
    validate(case.household, case.binding)
    validate_allocations(case)
    life_paths.validate(case)
    exchange_paths.validate(case)
    new_life_controls.validate(case)
    validate_options(case)
    drilling_controls.validate(case)
    qoz_controls.validate(case)
    data = case.household.model_dump(mode="json")
    binding = case.binding.model_dump(mode="json")
    data.update(
        target_age=case.targets.target_age,
        target_success=case.targets.success_fraction,
        reserve_years=case.targets.reserve_years,
    )
    for choice in selection:
        apply(data, binding, choice)
    allocate(data, binding, case.sleeve_opportunities, selections(selection))
    life_paths.apply(data, case.life_opportunities, life_paths.selections(selection))
    exchange_paths.apply(data, case.exchange_opportunities, exchange_paths.selected(selection))
    option_allocations.apply(
        data, binding, case.option_opportunity, option_allocations.selected(selection)
    )
    new_life_offers.apply(data, case.new_life_opportunities, new_life_controls.selected(selection))
    drilling_controls.apply(data, binding, case, selection)
    qoz_controls.apply(data, binding, case, selection)
    return Scenario.model_validate(data), HouseholdBinding.model_validate(binding)


def apply(data, binding, choice):
    retirement(data, choice)
    account_changes(data, choice)
    if choice.ira_orders is not None:
        if data["ira_plan"] is None:
            raise ValueError("IRA schedule choices require an existing configured IRA plan.")
        data["ira_plan"]["orders"] = [o.model_dump(mode="json") for o in choice.ira_orders]
    if choice.change_guardrail:
        binding["spending_guardrail"] = (
            choice.guardrail.model_dump(mode="json") if choice.guardrail else None
        )
    lot_changes(data, choice)


def lot_changes(data, choice):
    changes = (
        choice.sale_policies,
        choice.harvest_policies,
        choice.rebalances,
        choice.savings,
        choice.lot_funding_order,
    )
    if all(value is None for value in changes):
        return
    if data["lot_plan"] is None:
        raise ValueError(
            "Sale, harvest, rebalance, saving and funding-order choices require actual linked lots."
        )
    plan = data["lot_plan"]
    replace_schedules(plan, choice)
    reorder_funding(plan, choice.lot_funding_order)


def replace_schedules(plan, choice):
    owners = dict(
        sale_policies=plan["case"], harvest_policies=plan["case"], rebalances=plan, savings=plan
    )
    for key, owner in owners.items():
        value = getattr(choice, key)
        if value is not None:
            owner[key] = [p.model_dump(mode="json") for p in value]


def reorder_funding(plan, order):
    if order is None:
        return
    sources = plan["funding_sources"]
    if sorted(order) != list(range(len(sources))):
        raise ValueError("Funding order must be a permutation of existing source indices.")
    plan["funding_sources"] = [sources[i] for i in order]


def retirement(data, choice):
    members = {m["id"]: m for m in data["members"]}
    if not choice.retirement_dates.keys() <= members.keys():
        raise ValueError("Retirement choices must name existing household members.")
    for owner, day in choice.retirement_dates.items():
        members[owner]["retirement_date"] = day.isoformat()
