"""Dated supplied external flows and gross policy values, with no inferred scale."""

from datetime import date
from typing import Literal

from wealthlab.household.records import Money, Record
from wealthlab.tax.facts import TaxModel


class LifeFlow(Record):
    date: date
    kind: Literal[
        "premium",
        "dividend_cash",
        "withdrawal",
        "loan_advance",
        "loan_principal_repayment",
        "loan_interest_payment",
        "capitalized_interest",
        "external_fee",
    ]
    amount: Money


class LifeValue(TaxModel):
    date: date
    gross_cash_value: Money | None
    gross_surrender_value: Money | None
    gross_death_benefit: Money | None
