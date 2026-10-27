"""Explicit market bindings preserve tax character and the household cash boundary."""

from typing import Literal

from pydantic import Field

from wealthlab.household.records import Identifier
from wealthlab.markets.employer_inputs import EmployerBinding
from wealthlab.markets.guardrail_inputs import SpendingGuardrail
from wealthlab.markets.hsa_inputs import HSAInvestmentBinding
from wealthlab.markets.medical_inflation import MedicalBillIndexing
from wealthlab.markets.option_inputs import OptionBinding
from wealthlab.markets.wrapper_inputs import WrapperBinding
from wealthlab.tax.facts import TaxModel


class SecurityBinding(TaxModel):
    security_id: Identifier
    factor: Identifier
    federal_cash_character: Literal["dividends", "interest", "tax_exempt_interest"]
    nj_cash_character: Literal["dividends", "interest", "exempt"]


class HouseholdBinding(TaxModel):
    spending_guardrail: SpendingGuardrail | None = None
    options: OptionBinding | None = None
    securities: list[SecurityBinding] = Field(default_factory=list)
    hsa_securities: list[HSAInvestmentBinding] = Field(default_factory=list)
    replace_hsa_observations_confirmed: bool = False
    wrappers: list[WrapperBinding] = Field(default_factory=list)
    employers: list[EmployerBinding] = Field(default_factory=list)
    exchange_factors: dict[Identifier, Identifier] = Field(default_factory=dict)
    replace_exchange_observations_confirmed: bool = False
    sleeves: list[Identifier] = Field(default_factory=list)
    replace_sleeve_observations_confirmed: bool = False
    inflation_expenses: list[Identifier] = Field(default_factory=list)
    medical_bill_inflation: list[MedicalBillIndexing] = Field(default_factory=list)
    cash_yield_timing: Literal["opening_value_received_before_month_end_sales"]
    ordinary_cash_character_confirmed: bool
    other_accounts_unmodeled_returns_confirmed: bool
