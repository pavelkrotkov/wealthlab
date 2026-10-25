"""One separately owned option account uses actual household receipts and dated marks."""

from typing import Literal

from wealthlab.household.records import Identifier
from wealthlab.products.option_inputs import OptionCase
from wealthlab.tax.facts import TaxModel


class OptionPlan(TaxModel):
    account_id: Identifier
    case: OptionCase
    ordinary_dividend_tax_on_cash_receipt_confirmed: bool = False
    actual_household_cash_confirmed: bool
    tax_history_and_no_duplicate_income_confirmed: bool
    priority: Literal["after_prior_tax_arrears_before_sleeves_and_wrapper_deposits"]
