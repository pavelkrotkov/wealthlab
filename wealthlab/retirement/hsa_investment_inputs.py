"""Actual inside-HSA cash, positions and explicit conditional state recognition.

The existing lot book supplies share/cost arithmetic. Federal investment
income stays in the HSA; recipient withdrawals remain another cash movement.
State taxable-account treatment is an explicit assumption, not inferred from
federal exemption or a provider's marketing.
"""

from datetime import date
from typing import Literal

from pydantic import Field

from wealthlab.household.records import Identifier, Money, Record
from wealthlab.portfolio.cases import LotCase
from wealthlab.portfolio.household_inputs import HouseholdMarks
from wealthlab.portfolio.models import Price
from wealthlab.tax.facts import TaxModel


class HSAInvestmentLock(Record):
    security_id: Identifier
    start: date
    end: date


class HSACashTarget(Record):
    date: date
    account_id: Identifier
    amount: Money


class HSACashSource(TaxModel):
    account_id: Identifier
    security_id: Identifier
    selection: Literal["fifo", "hifo", "nj_hifo"]
    commission: Money


class HSAInvestments(TaxModel):
    case: LotCase
    opening_prices: dict[str, Price]
    marks: list[HouseholdMarks] = Field(default_factory=list)
    funding_sources: list[HSACashSource] = Field(default_factory=list)
    liquidity_locks: list[HSAInvestmentLock] = Field(default_factory=list)
    cash_targets: list[HSACashTarget] = Field(default_factory=list)
    nj_treatment: Literal["taxable_securities_no_wash_assumption"]
    complete_positions_and_state_basis_confirmed: bool
    conditional_state_treatment_confirmed: bool
    no_identical_outside_trading_confirmed: bool
    fees_are_custodian_charges_confirmed: bool
    ordinary_securities_no_ubti_confirmed: bool
