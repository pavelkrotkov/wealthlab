"""Explicit annual rules, dated recognized events and income-character mappings."""

from datetime import date
from decimal import Decimal
from typing import Annotated, Literal, Self

from pydantic import Field, model_validator

from wealthlab.household.records import Money
from wealthlab.tax.annual import AnnualCase
from wealthlab.tax.facts import FederalIncome, TaxModel
from wealthlab.tax.liquidation import FundingSource
from wealthlab.tax.nj_facts import NJIncome


class IncomeRule(TaxModel):
    income_id: str
    federal: Literal[
        "wages_primary",
        "wages_spouse",
        "interest",
        "dividends",
        "qualified_dividends",
        "ira_distributions",
        "taxable_pension",
        "social_security",
        "tax_exempt_interest",
        "ordinary_noninvestment_income",
        "none",
    ]
    new_jersey: Literal["wages", "interest", "dividends", "pension", "other", "none"]


class TaxEvent(TaxModel):
    date: date
    description: str = Field(min_length=1, max_length=200)
    cash_received: Money
    federal: FederalIncome
    new_jersey: NJIncome
    njbest_contributions: Money = Decimal(0)


class EstimatedPayment(TaxModel):
    date: date
    federal: Money
    new_jersey: Money


class TaxPlan(TaxModel):
    """Annual facts plus cash timing assumptions for one filing unit.

    Actual-payment deductions add NJ opening and newly paid amounts to the
    entered supplemental deduction. Refund fractions are keyed by source year;
    they are scenario assumptions, never inferred eligibility determinations.
    """

    cases: list[AnnualCase] = Field(min_length=1)
    income_rules: list[IncomeRule]
    events: list[TaxEvent] = Field(default_factory=list)
    estimated_payments: list[EstimatedPayment] = Field(default_factory=list)
    federal_wage_withholding: Decimal = Field(ge=0, le=1)
    nj_wage_withholding: Decimal = Field(ge=0, le=1)
    funding_sources: list[FundingSource] = Field(default_factory=list)
    settlement_timing: Literal["year_end", "monthly_accrued"] = "year_end"
    state_deduction_mode: Literal["actual_payments", "entered"] = "actual_payments"
    state_refund_taxable_fractions: dict[int, Annotated[Decimal, Field(ge=0, le=1)]] = Field(
        default_factory=dict
    )
    refund_month: int = Field(default=4, ge=1, le=12)

    @model_validator(mode="after")
    def unique_keys(self) -> Self:
        years = [case.policy.year for case in self.cases]
        rules = [rule.income_id for rule in self.income_rules]
        if len(years) != len(set(years)) or len(rules) != len(set(rules)):
            raise ValueError("Tax cases and income rules must have unique years/IDs.")
        return self
