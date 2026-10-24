"""Annual contribution forecasts with explicit compensation allocation and cash timing."""

from datetime import date
from typing import Literal, Self

from pydantic import Field, model_validator

from wealthlab.household.records import Account, Identifier, Money, Record
from wealthlab.retirement.contribution_assumptions import RuleMode
from wealthlab.tax.facts import SignedMoney, TaxModel


class Contributor(Record):
    birth_date: date
    eligible_ira_compensation: Money
    ira_compensation_budget: Money
    workplace_compensation: Money
    traditional_ira_magi: SignedMoney
    roth_ira_magi: SignedMoney
    covered_by_workplace_plan: bool
    prior_employer_wages: Money
    workplace_eligible: bool
    catchup_permitted: bool


class ContributionOrder(Record):
    date: date
    owner: Identifier
    destination: Identifier
    kind: Literal["traditional_ira", "roth_ira", "pretax_401k", "roth_401k"]
    amount: Money


class CashReceipt(Record):
    date: date
    amount: Money


class ContributionCase(TaxModel):
    year: int = Field(ge=2025, le=2200)
    rule_mode: RuleMode = "published"
    filing: Literal["single", "joint", "separate", "head", "surviving"]
    lived_with_spouse: bool
    spouse_covered_by_workplace_plan: bool
    opening_cash: Money
    contributors: list[Contributor] = Field(min_length=1, max_length=2)
    accounts: list[Account] = Field(min_length=1)
    receipts: list[CashReceipt] = Field(default_factory=list)
    orders: list[ContributionOrder] = Field(default_factory=list)

    @model_validator(mode="after")
    def references(self) -> Self:
        from wealthlab.retirement.contribution_validation import validate

        validate(self)
        return self
