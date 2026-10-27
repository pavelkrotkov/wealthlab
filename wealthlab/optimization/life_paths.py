"""Select complete supplied policy paths without interpolating an insurer illustration.

The original policy, opening equity, basis, debt and eligibility remain fixed.
Only fully specified future events/values and their corresponding failure exits
change. Native policy books still fund premiums and settle actual taxable cash.
"""

from pydantic import Field

from wealthlab.household.records import Record
from wealthlab.household.scenario import Scenario
from wealthlab.products.life_household_inputs import LifeHolding
from wealthlab.products.life_household_validation import validate as validate_native

PATH_FIELDS = {
    "name",
    "source",
    "source_date",
    "events",
    "values",
    "stop_funding_date",
    "values_match_executed_events_confirmed",
}


class LifePath(Record):
    holding: LifeHolding
    matched_path_terms_assumed_confirmed: bool = False
    explanation: str = Field(min_length=1, max_length=1000)


def control_keys(choice):
    return {"life_path:" + account for account in choice.life_paths or {}}


def selections(choices):
    selected = {}
    for choice in choices:
        value = choice.life_paths or {}
        if selected.keys() & value.keys():
            raise ValueError("Each policy account can have one controlling life-path dimension.")
        selected.update(value)
    return selected


def apply(data, offered, selected):
    paths = {path.id: path for path in offered}
    for account, identity in selected.items():
        path = paths.get(identity)
        if path is None or path.holding.account_id != account:
            raise ValueError("Life choices must name a supplied path for the selected account.")
        replace(data, path.holding)


def replace(data, holding):
    plan = data["life_plan"]
    if plan is None or holding.account_id not in {h["account_id"] for h in plan["holdings"]}:
        raise ValueError("Life-path choices require an existing configured policy account.")
    plan["holdings"] = [
        holding.model_dump(mode="json") if h["account_id"] == holding.account_id else h
        for h in plan["holdings"]
    ]


def validate(case):
    paths = case.life_opportunities
    if len({p.id for p in paths}) != len(paths):
        raise ValueError("Supplied life-path identifiers must be unique.")
    for path in paths:
        validate_path(case, path)
    offered = {p.id: p for p in paths}
    for dimension in case.dimensions:
        for choice in dimension.choices:
            validate_choice(choice, offered)


def validate_choice(choice, offered):
    for account, identity in (choice.life_paths or {}).items():
        if identity not in offered or offered[identity].holding.account_id != account:
            raise ValueError("Life choices must name a supplied path for that account.")


def validate_path(case, path):
    if path.provenance == "unresolved" or not path.matched_path_terms_assumed_confirmed:
        raise ValueError("Confirm the complete matched life-path terms and source.")
    original = case.household.life_plan
    holdings = {h.account_id: h for h in original.holdings} if original else {}
    baseline = holdings.get(path.holding.account_id)
    if baseline is None:
        raise ValueError("Life-path choices require an existing configured policy account.")
    validate_shared(baseline, path.holding)
    data = case.household.model_dump(mode="json")
    data["reserve_years"] = case.targets.reserve_years
    replace(data, path.holding)
    validate_native(Scenario.model_validate(data))


def validate_shared(original, proposed):
    if original.opening_values != proposed.opening_values or original.funding != proposed.funding:
        raise ValueError("Life choices must preserve opening values and funding permissions.")
    if original.contract.model_dump(exclude=PATH_FIELDS) != proposed.contract.model_dump(
        exclude=PATH_FIELDS
    ):
        raise ValueError("Life choices must preserve opening basis, loan and contract tax facts.")
