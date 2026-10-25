"""Reject ambiguous policy writes and unbounded work before execution.

The finite Cartesian product is the search boundary, not a sampling proposal.
A locked dimension still validates every declared option: malformed inactive
choices must not become executable merely by unlocking them later. Dimensions
own disjoint fields, and all choices within one dimension own the same fields;
there is no implicit last-write-wins ordering across unrelated policies."""

from math import prod

from wealthlab.household.calendar import months
from wealthlab.optimization.account_controls import AccountControls
from wealthlab.optimization.market_validation import validate_markets
from wealthlab.optimization.robustness_inputs import projection_paths
from wealthlab.optimization.robustness_inputs import validate as validate_robustness
from wealthlab.optimization.shared_terms import validate as validate_terms

FIELDS = (
    "sale_policies",
    "harvest_policies",
    "rebalances",
    "savings",
    "ira_orders",
    "lot_funding_order",
    *AccountControls.model_fields,
)


def choices(dimension):
    return [c for c in dimension.choices if dimension.locked_choice in (None, c.id)]


def footprint(choice):
    keys = {"retirement:" + key for key in choice.retirement_dates}
    keys.update(key for key in FIELDS if getattr(choice, key) is not None)
    if choice.change_guardrail:
        keys.add("guardrail")
    if choice.guardrail is not None and not choice.change_guardrail:
        raise ValueError("An entered guardrail requires an explicit change_guardrail choice.")
    if not keys:
        raise ValueError(
            "Each choice must name a controlled policy, including explicit empty schedules."
        )
    return keys


def validate(case):
    validate_markets(case)
    validate_terms(case)
    validate_robustness(case)
    identifiers, controlled = set(), set()
    for dimension in case.dimensions:
        if dimension.id in identifiers:
            raise ValueError("Dimension identifiers must be unique.")
        identifiers.add(dimension.id)
        keys = validate_dimension(dimension)
        if controlled & keys:
            raise ValueError(
                "Different dimensions cannot write the same policy or retirement date."
            )
        controlled.update(keys)
    count = prod(len(choices(d)) for d in case.dimensions)
    periods = len(list(months(case.household.start, case.household.end)))
    work = periods * (count * case.training.paths + case.validation.paths + projection_paths(case))
    if count > case.maximum_candidates or work > case.maximum_projection_months:
        raise ValueError("Search exceeds the explicit candidate or projection-month budget.")
    return count


def validate_dimension(dimension):
    ids = [c.id for c in dimension.choices]
    if len(ids) != len(set(ids)):
        raise ValueError("Choice identifiers must be unique within a dimension.")
    if dimension.locked_choice is not None and dimension.locked_choice not in ids:
        raise ValueError("A lock must name an allowed choice.")
    keys = footprint(dimension.choices[0])
    if any(footprint(c) != keys for c in dimension.choices):
        raise ValueError("Every choice in a dimension must control the same policy fields.")
    return keys
