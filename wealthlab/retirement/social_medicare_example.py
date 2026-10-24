"""Ordinary insured spouses with current Part B withholding and directly paid plan costs."""

from wealthlab.retirement.medicare_household_inputs import MedicarePlan
from wealthlab.retirement.medicare_household_template import template
from wealthlab.retirement.social_household_example import synthetic as household


def synthetic():
    case = household()
    payload = template(case)
    payload["collection_mode"] = "ssa_current_premiums"
    payload["ssa_current_premiums_context_confirmed"] = True
    payload["costs_excluded_from_other_expenses_confirmed"] = True
    payload["complete_household_tax_history_confirmed"] = True
    payload["case"]["complete_context"] = True
    for coverage in payload["case"]["coverage"]:
        coverage["eligibility_confirmed"] = True
    return case.model_copy(
        update=dict(
            name="Synthetic Social Security and Medicare withholding",
            medicare_plan=MedicarePlan.model_validate(payload),
        )
    )
