"""Reuse dated household accruals by splitting wage schedules at actual decision dates.

Growth retains the original scenario-time origin. A pay multiplier applies to
the baseline stream, not the preceding event's pay. Member retirement cutoffs
remain effective, and the immutable exported source retains every decision.
"""

from decimal import Decimal
from itertools import pairwise

from wealthlab.employment.validation import validate
from wealthlab.household.calendar import money


def prepare(scenario):
    if scenario.employment_plan is None:
        return scenario
    validate(scenario)
    paths = {
        identifier: path
        for path in scenario.employment_plan.paths
        for identifier in path.income_ids
    }
    rules = {r.income_id: r for r in scenario.tax_plan.income_rules}
    incomes, mapped = [], []
    for index, income in enumerate(scenario.incomes):
        path = paths.get(income.id)
        pieces = [income] if path is None else split(income, path, index)
        incomes.extend(pieces)
        mapped.extend(rules[income.id].model_copy(update=dict(income_id=p.id)) for p in pieces)
    plan = scenario.tax_plan.model_copy(update=dict(income_rules=mapped))
    payload = scenario.model_dump()
    payload.update(incomes=incomes, tax_plan=plan, employment_plan=None)
    return type(scenario).model_validate(payload)


def split(income, path, index):
    changes = list(effective_changes(path))
    dates = [
        income.start,
        *(e.date for e in changes if income.start < e.date < income.end),
        income.end,
    ]
    result = []
    for part, (start, end) in enumerate(pairwise(dates)):
        multiplier = at(changes, start, path.opening_multiplier)
        result.append(
            income.model_copy(
                update=dict(
                    id=f"employment_{index}_{part}",
                    start=start,
                    end=end,
                    monthly_amount=money(income.monthly_amount * multiplier),
                )
            )
        )
    return result


def at(changes, when, opening: Decimal):
    eligible = [change for change in changes if change.date <= when]
    return eligible[-1].multiplier if eligible else opening


def effective_changes(path):
    # A no-op must not split one cash flow into separately rounded fragments.
    previous = path.opening_multiplier
    for change in sorted(path.changes, key=lambda e: e.date):
        if change.multiplier != previous:
            yield change
            previous = change.multiplier
