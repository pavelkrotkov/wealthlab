"""Household 529 deposits and separate, confirmed qualified institution bills."""

from datetime import date

from pydantic import Field

from wealthlab.household.records import Identifier, Money, Record
from wealthlab.retirement.account_liquidity import AccountLock
from wealthlab.retirement.contribution_assumptions import RuleMode
from wealthlab.retirement.distribution_inputs import AccountReturn
from wealthlab.retirement.education_inputs import (
    EducationContribution,
    EducationPerson,
    EducationPlan,
)
from wealthlab.tax.facts import TaxModel


class EducationAccountTerms(TaxModel):
    account_id: Identifier
    beneficiary: Identifier
    plan: Identifier
    contribution_basis: Money


class TuitionPayment(Record):
    date: date
    source: Identifier
    amount: Money


class EducationHouseholdPlan(TaxModel):
    rule_mode: RuleMode
    people: list[EducationPerson]
    plans: list[EducationPlan]
    accounts: list[EducationAccountTerms]
    contributions: list[EducationContribution]
    tuition: list[TuitionPayment]
    liquidity_locks: list[AccountLock] = Field(default_factory=list)
    returns: list[AccountReturn]
    complete_context_confirmed: bool
    qualified_net_expenses_separate_from_other_budgets_confirmed: bool
    contributions_belong_to_filing_unit_confirmed: bool
