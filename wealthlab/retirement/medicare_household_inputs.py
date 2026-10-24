"""Direct-billed Medicare costs share the household wallet and completed tax history."""

from typing import Literal

from wealthlab.retirement.medicare_inputs import MedicareCase
from wealthlab.tax.facts import TaxModel


class MedicarePlan(TaxModel):
    case: MedicareCase
    collection_mode: Literal["direct_bill_only", "ssa_current_premiums"] = "direct_bill_only"
    ssa_current_premiums_context_confirmed: bool = False
    direct_billing_without_benefit_withholding_confirmed: bool
    costs_excluded_from_other_expenses_confirmed: bool
    complete_household_tax_history_confirmed: bool


def withholding(scenario):
    plan = scenario.medicare_plan
    return plan is not None and plan.collection_mode == "ssa_current_premiums"
