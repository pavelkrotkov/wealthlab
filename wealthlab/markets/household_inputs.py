"""Explicit market bindings preserve tax character and the household cash boundary."""

from typing import Literal

from pydantic import Field

from wealthlab.household.records import Identifier
from wealthlab.markets.guardrail_inputs import SpendingGuardrail
from wealthlab.tax.facts import TaxModel


class SecurityBinding(TaxModel):
    security_id: Identifier
    factor: Identifier
    federal_cash_character: Literal["dividends", "interest", "tax_exempt_interest"]
    nj_cash_character: Literal["dividends", "interest", "exempt"]


class HouseholdBinding(TaxModel):
    spending_guardrail: SpendingGuardrail | None = None
    securities: list[SecurityBinding] = Field(min_length=1)
    inflation_expenses: list[Identifier] = Field(default_factory=list)
    cash_yield_timing: Literal["opening_value_received_before_month_end_sales"]
    ordinary_cash_character_confirmed: bool
    other_accounts_unmodeled_returns_confirmed: bool
