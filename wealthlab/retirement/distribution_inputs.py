"""IRA-only annual reconciliation; cash events are dated and schedules are fixed."""

from datetime import date
from decimal import Decimal
from typing import Annotated, Literal, Self

from pydantic import Field, model_validator

from wealthlab.household.records import Account, Identifier, Money, Record
from wealthlab.retirement.account_liquidity import AccountLock
from wealthlab.retirement.contribution_inputs import ContributionCase
from wealthlab.retirement.ira_rollover_inputs import IncomingIRARollover
from wealthlab.tax.annual import AnnualCase
from wealthlab.tax.facts import TaxModel


class ConversionBalance(TaxModel):
    year: int = Field(ge=1998, le=2200)
    taxable_remaining: Money
    nontaxable_remaining: Money


class DistributionOwner(Record):
    """Basis is aggregated across this owner's ordinary IRA accounts.

    Conversion entries are remaining prior-year amounts, split by the amount
    originally taxable federally. NJ Roth basis has its own independent history.
    """

    birth_date: date
    federal_ira_basis: Money
    nj_ira_basis: Money
    roth_regular_basis: Money
    nj_roth_basis: Money
    roth_first_year: int | None = Field(default=None, ge=1998, le=2200)
    conversions: list[ConversionBalance] = Field(default_factory=list)
    birth_1959_start_age: Literal[73, 75] | None = None
    rmd_table: Literal["uniform", "sole_younger_spouse"]
    spouse_birth_date: date | None = None


class IRAAccount(Account):
    product: Literal["traditional_ira", "roth_ira"]


class WithdrawalOrder(Record):
    date: date
    source: Identifier
    destination: Identifier | None = None
    kind: Literal["withdrawal", "conversion"]
    amount: Money
    early_penalty_exception: bool


class AccountReturn(Record):
    date: date
    account_id: Identifier
    rate: Annotated[Decimal, Field(ge=-1, le=10, max_digits=18, decimal_places=12)]


class DistributionCase(TaxModel):
    year: int = Field(ge=2025, le=2200)
    opening_cash: Money
    opening_context_complete: bool
    owners: list[DistributionOwner] = Field(min_length=1, max_length=2)
    accounts: list[IRAAccount] = Field(min_length=1)
    nj_treatment: Literal["resident_combined_owner_pools"]
    rmd_policy: Literal["december_target_no_deferral"]
    orders: list[WithdrawalOrder] = Field(default_factory=list)
    incoming_rollovers: list[IncomingIRARollover] = Field(default_factory=list)
    returns: list[AccountReturn] = Field(default_factory=list)
    liquidity_locks: list[AccountLock] = Field(default_factory=list)
    annual_tax_case: AnnualCase | None = None
    contributions: ContributionCase | None = None
    contribution_context_confirmed: bool = False

    @model_validator(mode="after")
    def references(self) -> Self:
        from wealthlab.retirement.distribution_validation import validate

        validate(self)
        return self
