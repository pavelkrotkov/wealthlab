"""Annual savings-type 529 projections with explicit expense and recipient allocation."""

from datetime import date
from decimal import Decimal
from typing import Annotated, Literal, Self

from pydantic import Field, model_validator

from wealthlab.household.records import Account, Identifier, Money, Record
from wealthlab.retirement.account_liquidity import AccountLock
from wealthlab.retirement.contribution_assumptions import RuleMode
from wealthlab.retirement.contribution_inputs import CashReceipt
from wealthlab.retirement.distribution_inputs import AccountReturn
from wealthlab.tax.facts import TaxModel


class EducationPerson(Record):
    household_cash_member: bool


class PlanLimit(TaxModel):
    effective: date
    maximum_balance: Money


class EducationPlan(Record):
    njbest: bool
    limits: list[PlanLimit] = Field(min_length=1)


class EducationAccount(Account):
    wrapper: Literal["education"]
    currency: Literal["USD"]
    monthly_fee: Annotated[Money, Field(le=0)]
    beneficiary: Identifier
    plan: Identifier
    contribution_basis: Money
    zero_value_basis_history_confirmed: bool = False

    @model_validator(mode="after")
    def empty_balance(self) -> Self:
        if (
            not self.balance
            and self.contribution_basis
            and not self.zero_value_basis_history_confirmed
        ):
            raise ValueError("An empty opening 529 cannot retain closed-account basis.")
        return self


class EducationContribution(Record):
    date: date
    destination: Identifier
    amount: Money


class EducationWithdrawal(Record):
    date: date
    source: Identifier
    amount: Money
    payee: Literal["owner", "beneficiary", "institution"]


class EducationExpense(Record):
    """Expense payments are recorded outside this isolated reimbursement workbench.

    Confirm institution, enrollment, room/board caps and eligible expense type
    before classifying a higher-education amount as qualified. Other benefits
    reserve their expenses first; only the remaining amount can support a 529.
    """

    beneficiary: Identifier
    paid: date
    amount: Money
    tax_free_aid: Money
    credit_expenses: Money
    other_vehicle_expenses: Money
    eligibility: Literal["confirmed_higher_education", "not_qualified"]


class EducationUse(TaxModel):
    expense: Identifier
    amount: Money


class EducationAllocation(Record):
    account: Identifier
    recipient: Literal["owner", "beneficiary"]
    expenses: list[EducationUse] = Field(default_factory=list)
    additional_tax_exempt_earnings: Money = Decimal(0)
    nj_recaptured_contributions: Money | None = None


class EducationCase(TaxModel):
    year: int = Field(ge=2025, le=2200)
    rule_mode: RuleMode = "published"
    opening_cash: Money
    complete_context: bool
    nj_gross_income: Money | None
    people: list[EducationPerson] = Field(min_length=1)
    plans: list[EducationPlan] = Field(min_length=1)
    accounts: list[EducationAccount] = Field(min_length=1)
    receipts: list[CashReceipt] = Field(default_factory=list)
    contributions: list[EducationContribution] = Field(default_factory=list)
    withdrawals: list[EducationWithdrawal] = Field(default_factory=list)
    returns: list[AccountReturn] = Field(default_factory=list)
    liquidity_locks: list[AccountLock] = Field(default_factory=list)
    expenses: list[EducationExpense] = Field(default_factory=list)
    allocations: list[EducationAllocation] = Field(default_factory=list)

    @model_validator(mode="after")
    def references(self) -> Self:
        from wealthlab.retirement.education_validation import validate

        validate(self)
        return self
