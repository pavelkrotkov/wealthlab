"""Atomic whole-illustration selections reuse the native zero-opening offer validator.

None preserves the baseline; an explicit empty list chooses no new issues.
All offered contracts validate before any candidate or lock can select them.
Existing policies and independently supplied protection needs remain unchanged.
"""

from wealthlab.optimization.new_life_offers import selected_offers, validate_offers


def validate(case):
    household = case.household.model_copy(update={"reserve_years": case.targets.reserve_years})
    validate_offers(household, case.new_life_opportunities)
    for dimension in case.dimensions:
        for choice in dimension.choices:
            selected_offers(case.new_life_opportunities, choice.new_life_purchases or [])


def selected(choices):
    values = [c.new_life_purchases for c in choices if c.new_life_purchases is not None]
    if len(values) > 1:
        raise ValueError("Only one dimension can control the new-policy purchase set.")
    return values[0] if values else []
