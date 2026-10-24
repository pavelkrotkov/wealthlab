"""Cash-only HSA forecasts share household cash and historical qualified receipts."""

from decimal import Decimal
from typing import Annotated, Literal

from pydantic import Field

from wealthlab.household.records import Identifier
from wealthlab.retirement.contribution_assumptions import RuleMode
from wealthlab.retirement.hsa_inputs import (
    HSAContribution,
    HSAInterest,
    HSAOwner,
    HSAWithdrawal,
    MedicalReceipt,
)
from wealthlab.tax.facts import TaxModel

Fraction = Annotated[Decimal, Field(ge=0, le=1, max_digits=18, decimal_places=12)]


class HSAHouseholdYear(TaxModel):
    year: int = Field(ge=2025, le=2200)
    rule_mode: RuleMode = "published"
    married: bool
    owners: list[HSAOwner] = Field(min_length=1, max_length=2)


class HSAPlan(TaxModel):
    years: list[HSAHouseholdYear] = Field(min_length=1)
    medical_receipts: list[MedicalReceipt]
    contributions: list[HSAContribution]
    withdrawals: list[HSAWithdrawal]
    interest: list[HSAInterest]
    nj_treatment: Literal["taxable_bank_interest_assumption"]
    conditional_nj_treatment_confirmed: bool
    cash_only_accounts_and_complete_context_confirmed: bool
    receipts_paid_before_projection_confirmed: bool
    employer_funding_excluded_from_other_nj_wages_confirmed: bool
    priority: Literal["after_receipts_before_ira_and_current_tax"]
    nonqualified_treatment: Literal["unconfirmed", "ordinary_noninvestment_assumption"] = (
        "unconfirmed"
    )
    nj_withdrawal_taxable_fractions: dict[Identifier, Fraction] = Field(default_factory=dict)
    generated_distribution_tax_excluded_from_other_inputs_confirmed: bool = False
