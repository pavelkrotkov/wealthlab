"""Every offered unit validates even when the only active choice buys zero.

The temporary one-unit household checks native ownership, dates, tax assumptions
and each market's configured execution scope. It is never projected or ranked.
One native path per market is sufficient for its supplied calendar/yield/lock
preflight; all realized candidate paths still run native execution validation.
"""

from wealthlab.household.scenario import Scenario
from wealthlab.markets.household_inputs import HouseholdBinding
from wealthlab.markets.option_validation import validate as validate_market
from wealthlab.markets.paths import generate
from wealthlab.optimization.option_allocations import insert
from wealthlab.products.option_allocation import scale_new_plan
from wealthlab.products.option_household_validation import validate as validate_native


def validate(case):
    item = case.option_opportunity
    counts = offered_counts(case)
    if item is None:
        if counts:
            raise ValueError("Every option allocation requires a supplied opportunity.")
        return
    if not counts or any(not item.minimum_units <= n <= item.maximum_units for n in counts):
        raise ValueError("Every option choice must respect the supplied opportunity bounds.")
    validate_source(case, item)
    plan = scale_new_plan(
        item.unit, 1, per_unit_fees_confirmed=item.per_unit_absolute_fees_confirmed
    )
    data, binding = case.household.model_dump(mode="json"), case.binding.model_dump(mode="json")
    insert(data, binding, item, plan)
    scenario = Scenario.model_validate(data)
    validate_native(scenario, None)
    validate_wash_groups(case.household, item.unit)
    linked = HouseholdBinding.model_validate(binding)
    markets = [case.training, case.validation, *(c.market for c in case.robustness.values())]
    for market in markets:
        validate_market(scenario, generate(market.model_copy(update={"paths": 1})), linked)


def validate_source(case, item):
    if item.provenance == "unresolved" or not item.opening_cash_purchase_assumed_confirmed:
        raise ValueError("Confirm the sourced new option purchase assumptions.")
    source = next((a for a in case.household.accounts if a.id == item.cash_account), None)
    if source is None or (source.wrapper, source.currency) != ("cash", "USD"):
        raise ValueError("New option purchases require an existing USD cash account.")
    validate_owner(case.household, item)


def validate_owner(household, item):
    owners = {"primary": household.members[0].id, "joint": "joint"}
    if len(household.members) == 2:
        owners["spouse"] = household.members[1].id
    if item.owner != owners.get(item.unit.case.holdings.accounts[0].owner):
        raise ValueError("Map the native option owner role to the same household owner.")


def validate_wash_groups(household, plan):
    groups = {s.wash_group for s in plan.case.holdings.securities}
    books = [household.lot_plan.case] if household.lot_plan else []
    if household.hsa_plan and household.hsa_plan.investments:
        books.append(household.hsa_plan.investments.case)
    if any(groups & {s.wash_group for s in book.securities} for book in books):
        raise ValueError("New option books need distinct wash groups from linked lot/HSA books.")


def offered_counts(case):
    return [
        c.option_units for d in case.dimensions for c in d.choices if c.option_units is not None
    ]
