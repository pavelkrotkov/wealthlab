"""Direct-billed Medicare costs share the household wallet and completed tax history."""

from wealthlab.retirement.medicare_inputs import MedicareCase
from wealthlab.tax.facts import TaxModel


class MedicarePlan(TaxModel):
    case: MedicareCase
    direct_billing_without_benefit_withholding_confirmed: bool
    costs_excluded_from_other_expenses_confirmed: bool
    complete_household_tax_history_confirmed: bool
