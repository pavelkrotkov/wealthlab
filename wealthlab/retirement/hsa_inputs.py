"""Cash-only HSA funding with monthly eligibility and a shared receipt ledger."""

from datetime import date
from decimal import Decimal
from typing import Annotated, Literal, Self

from pydantic import Field, model_validator

from wealthlab.household.records import Account, Identifier, Money, Record
from wealthlab.retirement.contribution_inputs import CashReceipt
from wealthlab.tax.facts import TaxModel


class HSAMonth(TaxModel):
    month: int = Field(ge=1, le=12)
    coverage: Literal["none", "self", "family"]
    disqualifying_coverage: bool
    medicare: bool
    claimable_dependent: bool
    family_share: Annotated[Decimal, Field(ge=0, le=1)] | None = None


class HSAOwner(Record):
    birth_date: date
    established: date
    disabled_since: date | None = None
    months: list[HSAMonth] = Field(min_length=12, max_length=12)


class MedicalReceipt(Record):
    """These expenses are already paid; this workbench does not pay them again.

    One shared receipt can be eligible for multiple owners, but its reimbursed
    balance is global. Amounts deducted federally are unavailable to a later
    tax-free HSA reimbursement, even when the expense is otherwise qualified.
    """

    eligible_owners: list[Identifier] = Field(min_length=1, max_length=2)
    incurred: date
    paid: date
    amount: Money
    reimbursed_elsewhere: Money
    deducted_federally: Money
    eligibility: Literal["qualified_medical", "not_qualified", "unresolved"]


class HSAContribution(Record):
    date: date
    destination: Identifier
    source: Literal["personal_cash", "direct_employer"]
    amount: Money


class HSAWithdrawal(Record):
    date: date
    source: Identifier
    amount: Money
    mode: Literal["qualified_only", "allow_nonqualified"]
    receipt_ids: list[Identifier] = Field(default_factory=list)


class HSAInterest(Record):
    date: date
    account_id: Identifier
    taxable_bank_interest: Money


class HSACase(TaxModel):
    year: Literal[2025, 2026]
    opening_cash: Money
    married: bool
    complete_context: bool
    contribution_policy: Literal["monthly_only"]
    nj_treatment: Literal["unconfirmed", "taxable_bank_interest_assumption"]
    owners: list[HSAOwner] = Field(min_length=1, max_length=2)
    accounts: list[Account] = Field(min_length=1)
    cash_receipts: list[CashReceipt] = Field(default_factory=list)
    medical_receipts: list[MedicalReceipt] = Field(default_factory=list)
    contributions: list[HSAContribution] = Field(default_factory=list)
    withdrawals: list[HSAWithdrawal] = Field(default_factory=list)
    interest: list[HSAInterest] = Field(default_factory=list)

    @model_validator(mode="after")
    def references(self) -> Self:
        from wealthlab.retirement.hsa_validation import validate

        validate(self)
        return self
