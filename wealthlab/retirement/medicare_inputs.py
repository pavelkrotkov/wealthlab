"""Dated Medicare coverage, income history and explicit future premium assumptions."""

from datetime import date
from decimal import Decimal
from typing import Annotated, Literal, Self

from pydantic import Field, model_validator

from wealthlab.household.records import Identifier, Money, Record
from wealthlab.retirement.contribution_inputs import CashReceipt
from wealthlab.tax.facts import SignedMoney, TaxModel

Growth = Annotated[Decimal, Field(ge=0, le="0.30", max_digits=8, decimal_places=6)]


class MedicareIncome(Record):
    """Members share one return's MAGI; joint income is not divided between spouses."""

    year: int = Field(ge=2023, le=2200)
    members: list[Identifier] = Field(min_length=1, max_length=2)
    filing: Literal["individual", "joint", "separate_lived_together", "separate_lived_apart"]
    agi: SignedMoney
    tax_exempt_interest: Money


class MedicareCoverage(Record):
    member: Identifier
    start: date
    end: date
    eligibility_confirmed: bool
    part_a: bool
    part_a_monthly_2026: Money
    part_b: bool
    standard_b_premium_applicable: bool
    part_d: bool
    part_d_plan_monthly_2026: Money
    other_monthly_health_cost_2026: Money


class MedicareDetermination(Record):
    member: Identifier
    premium_year: int = Field(ge=2026, le=2200)
    income: Identifier
    method: Literal["three_year_fallback_confirmed", "conditional_ssa_redetermination"]


class MedicareCase(TaxModel):
    start_year: int = Field(ge=2026, le=2200)
    end_year: int = Field(ge=2027, le=2201)
    opening_cash: Money
    complete_context: bool
    future_policy: Literal["freeze_2026", "index_2026_assumption"]
    premium_growth: Growth
    threshold_growth: Growth
    payment_policy: Literal["first_of_coverage_month_fifo_arrears"]
    members: list[Record] = Field(min_length=1)
    coverage: list[MedicareCoverage] = Field(min_length=1)
    income_history: list[MedicareIncome] = Field(default_factory=list)
    determinations: list[MedicareDetermination] = Field(default_factory=list)
    receipts: list[CashReceipt] = Field(default_factory=list)

    @model_validator(mode="after")
    def references(self) -> Self:
        from wealthlab.retirement.medicare_validation import validate

        validate(self)
        return self
