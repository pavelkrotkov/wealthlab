"""A liquid alternative must preserve starting capital and price protection separately.

Zero-value insurance accounts may differ, allowing newly issued term versus
whole life. Existing positive-equity policies remain present with the same
opening value and require an actual supplied surrender in the liquid reference.
"""

from wealthlab.products.life_comparison_history import history
from wealthlab.products.life_comparison_reference import validate_reference

EXCLUDED = {"name", "life_plan", "lot_plan", "accounts"}


def validate(case):
    if case.liquid_reference not in case.alternatives:
        raise ValueError("Name an existing liquid-saving reference alternative.")
    if not case.independently_priced_protection_confirmed:
        raise ValueError(
            "Confirm an independently supplied protection price and coverage schedule."
        )
    if (case.market is None) != (case.binding is None):
        raise ValueError("Supply both shared market inputs and their household bindings.")
    reference = case.alternatives[case.liquid_reference]
    plans(reference)
    for scenario in case.alternatives.values():
        plans(scenario)
        matched(reference, scenario)
    validate_reference(case, reference)


def matched(reference, scenario):
    if scenario.model_dump(exclude=EXCLUDED) != reference.model_dump(exclude=EXCLUDED):
        raise ValueError(
            "Insurance alternatives require identical household/tax/spending background."
        )
    if scenario.life_plan.insurance_need_by_owner != reference.life_plan.insurance_need_by_owner:
        raise ValueError("Use the same independent insurance needs across alternatives.")
    if scenario.lot_plan.model_dump(exclude={"savings"}) != reference.lot_plan.model_dump(
        exclude={"savings"}
    ):
        raise ValueError(
            "Alternative lot books and observations must differ only in saving budgets."
        )
    if opening_accounts(reference) != opening_accounts(scenario):
        raise ValueError("Preserve all household capital and existing policy opening equity.")

    if history(reference) != history(scenario):
        raise ValueError("Preserve existing opening policy history across alternatives.")


def plans(scenario):
    if scenario.life_plan is None or scenario.lot_plan is None:
        raise ValueError("Every alternative requires policy and liquid-saving lot plans.")


def opening_accounts(scenario):
    return {
        a.id: a.model_dump() for a in scenario.accounts if a.wrapper != "insurance" or a.balance > 0
    }
