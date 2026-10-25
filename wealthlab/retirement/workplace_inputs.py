"""Explicit employee 401(k) elections, without inferring employer or plan eligibility."""

from datetime import date
from typing import Literal

from pydantic import Field

from wealthlab.household.records import Identifier, Money, Record
from wealthlab.retirement.account_liquidity import AccountLock
from wealthlab.retirement.contribution_assumptions import RuleMode
from wealthlab.retirement.contribution_inputs import ContributionOrder
from wealthlab.retirement.distribution_inputs import AccountReturn
from wealthlab.retirement.workplace_withdrawal_inputs import WorkplaceCashPlan
from wealthlab.tax.facts import TaxModel


class WorkplaceContributor(Record):
    birth_date: date
    workplace_compensation: Money
    prior_employer_wages: Money
    workplace_eligible: bool
    catchup_permitted: bool


class WorkplaceYear(TaxModel):
    year: int = Field(ge=2025, le=2200)
    rule_mode: RuleMode = "published"
    contributors: list[WorkplaceContributor] = Field(min_length=1, max_length=2)


class WorkplaceOrder(ContributionOrder):
    kind: Literal["pretax_401k", "roth_401k"]


class WorkplacePlan(TaxModel):
    years: list[WorkplaceYear] = Field(min_length=1)
    products: dict[Identifier, Literal["pretax_401k", "roth_401k"]]
    orders: list[WorkplaceOrder]
    cash_withdrawals: WorkplaceCashPlan | None = None
    returns: list[AccountReturn] = Field(default_factory=list)
    liquidity_locks: list[AccountLock] = Field(default_factory=list)
    complete_single_employer_elections_confirmed: bool
    gross_wages_before_deferrals_confirmed: bool
    timing: Literal["monthly_payroll_before_tax_and_spending"]
