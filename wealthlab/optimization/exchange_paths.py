"""Select complete sourced contribution/exit paths for the same original stock.

Tax eligibility, fees, baskets, source basis and holding history remain fixed.
Each path supplies its own complete dollar flows; no K-1 scaling or legal
eligibility calculation is inferred from a chosen contribution quantity.
"""

from datetime import date

from pydantic import Field

from wealthlab.household.records import Record
from wealthlab.household.scenario import Scenario
from wealthlab.markets.exchange_compile import compile_plan
from wealthlab.markets.exchange_compile import validate as validate_binding
from wealthlab.markets.paths import generate
from wealthlab.products.exchange_fund_inputs import ExchangeFundPlan
from wealthlab.products.exchange_fund_validation import validate as validate_native

PATH_FIELDS = {"contribution_quantity", "mode", "observations", "requests"}
FLOW_FIELDS = {"distribution", "federal_basis_adjustment", "nj_basis_adjustment", "allocation"}


class ExchangePath(Record):
    plan: ExchangeFundPlan
    source: str = Field(min_length=1, max_length=1000)
    available_on: date
    complete_cash_tax_and_basis_profile_confirmed: bool = False
    profile_valid_for_projected_income_and_market_paths_confirmed: bool = False


def control_keys(choice):
    return {"exchange_plan"} if choice.exchange_path is not None else set()


def selected(choices):
    values = [c.exchange_path for c in choices if c.exchange_path is not None]
    if len(values) > 1:
        raise ValueError("Only one dimension can control the exchange contribution path.")
    return values[0] if values else None


def apply(data, offered, identity):
    if identity is None:
        return
    path = next((p for p in offered if p.id == identity), None)
    if path is None:
        raise ValueError("Exchange choices must name a supplied contribution path.")
    data["exchange_fund_plan"] = path.plan.model_dump(mode="json")


def validate(case):
    offered = {p.id: p for p in case.exchange_opportunities}
    if len(offered) != len(case.exchange_opportunities):
        raise ValueError("Exchange path identifiers must be unique.")
    for path in offered.values():
        validate_path(case, path)
    for dimension in case.dimensions:
        for choice in dimension.choices:
            if choice.exchange_path is not None and choice.exchange_path not in offered:
                raise ValueError("Every exchange choice must name a supplied path.")


def validate_path(case, path):
    if path.provenance == "unresolved" or not path.source.strip():
        raise ValueError("Provide a resolved source for each exchange contribution profile.")
    if not (
        path.complete_cash_tax_and_basis_profile_confirmed
        and path.profile_valid_for_projected_income_and_market_paths_confirmed
    ):
        raise ValueError("Confirm complete exchange facts valid across this projected envelope.")
    if path.available_on > case.household.start:
        raise ValueError("Exchange profile sources must be available at the opening decision.")
    original = case.household.exchange_fund_plan
    if original is None:
        raise ValueError("Exchange paths require an existing original source book.")
    validate_shared(original, path.plan)
    data = case.household.model_dump(mode="json")
    data["exchange_fund_plan"] = path.plan.model_dump(mode="json")
    household = Scenario.model_validate(data)
    validate_native(household)
    validate_markets(case, household)


def validate_shared(original, proposed):
    if original.model_dump(exclude=PATH_FIELDS) != proposed.model_dump(exclude=PATH_FIELDS):
        raise ValueError("Keep exchange source stock, basis, eligibility, basket and fees fixed.")
    left = [o.model_dump(exclude=FLOW_FIELDS) for o in original.observations]
    right = [o.model_dump(exclude=FLOW_FIELDS) for o in proposed.observations]
    if left != right:
        raise ValueError("Keep exchange observation dates, source prices and locks fixed.")
    original_rules = [
        o.allocation.model_dump(exclude={"federal", "new_jersey"}) for o in original.observations
    ]
    proposed_rules = [
        o.allocation.model_dump(exclude={"federal", "new_jersey"}) for o in proposed.observations
    ]
    if original_rules != proposed_rules:
        raise ValueError("Exchange allocation eligibility and recognition dates must stay fixed.")


def validate_markets(case, household):
    if not case.binding.exchange_factors:
        raise ValueError("Exchange paths require explicit source and basket factor bindings.")
    markets = [case.training, case.validation, *(c.market for c in case.robustness.values())]
    for market in markets:
        batch = generate(market.model_copy(update={"paths": 1}))
        validate_binding(household, batch, case.binding)
        compiled = household.model_dump(mode="json")
        compile_plan(compiled, household, batch, case.binding, 0)
