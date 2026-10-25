"""HSA factors preserve actual shares and independent conditional NJ cash character."""

from typing import Literal

from wealthlab.household.records import Identifier
from wealthlab.tax.facts import TaxModel


class HSAInvestmentBinding(TaxModel):
    security_id: Identifier
    factor: Identifier
    nj_cash_character: Literal["dividends", "interest", "exempt"]
