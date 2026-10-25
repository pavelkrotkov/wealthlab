"""An executed event keeps gross settlement distinct from external cash.

For surrender/lapse, amount includes loan satisfaction. Pre-event cash value is
before surrender charges; NJ income is a separately supplied ordinary category,
not a federal basis proxy or inferred eligibility for a state pension exclusion.
"""

from datetime import date
from typing import Literal

from wealthlab.household.records import Money, Record


class PolicyEvent(Record):
    date: date
    kind: Literal[
        "premium",
        "withdrawal",
        "dividend_cash",
        "loan_advance",
        "capitalized_interest",
        "loan_principal_repayment",
        "loan_interest_payment",
        "external_fee",
        "surrender",
        "lapse",
    ]
    amount: Money
    cash_value_before: Money | None = None
    nj_ordinary_income: Money | None = None
