"""Versioned scenario validation and explicit first-year opening context.

Nested rule plans remain immutable source inputs. Projection adapters produce
dated salary and benefit flows in a copy; exports keep the original plans so
reloading cannot count generated income as a second independent cash source.
"""

from datetime import date
from typing import Annotated, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from wealthlab.employment.compensation_inputs import CompensationPlan
from wealthlab.employment.inputs import EmploymentPlan
from wealthlab.household.advisory_inputs import AdvisoryPlan
from wealthlab.household.records import Account, Member, Money
from wealthlab.household.schedules import Contribution, Debt, Expense, Income
from wealthlab.household.validation import validate_dates, validate_references
from wealthlab.portfolio.household_inputs import HouseholdLots
from wealthlab.products.exchange_fund_inputs import ExchangeFundPlan
from wealthlab.products.household_inputs import SleevePlan
from wealthlab.products.life_household_inputs import LifeHouseholdPlan
from wealthlab.products.life_household_records import validate_ownership as validate_life_ownership
from wealthlab.products.option_household_inputs import OptionPlan
from wealthlab.products.qoz_inputs import QOZPlan
from wealthlab.retirement.education_household_inputs import EducationHouseholdPlan
from wealthlab.retirement.hsa_household_inputs import HSAPlan
from wealthlab.retirement.ira_household_inputs import IRAPlan
from wealthlab.retirement.medicare_household_inputs import MedicarePlan
from wealthlab.retirement.social_inputs import SocialCase
from wealthlab.retirement.social_work_inputs import WorkPolicy
from wealthlab.retirement.workplace_inputs import WorkplacePlan
from wealthlab.tax.projection_inputs import TaxPlan


class YearToDate(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, allow_inf_nan=False)
    gross_income: Money
    federal_tax_paid: Money
    state_tax_paid: Money


class Scenario(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, allow_inf_nan=False)
    schema_version: Literal[1]
    name: str = Field(min_length=1, max_length=120)
    synthetic: bool
    start: date
    end: date
    inflation: float = Field(ge=-0.5, le=1)
    usd_per_currency: dict[str, Annotated[float, Field(gt=0, le=1000000)]]
    reserve_years: float = Field(ge=0, le=20)
    target_success: float = Field(gt=0, le=1)
    target_age: int = Field(ge=50, le=120)
    ytd: YearToDate
    members: list[Member] = Field(min_length=1, max_length=2)
    accounts: list[Account] = Field(min_length=1)
    incomes: list[Income]
    expenses: list[Expense]
    debts: list[Debt]
    contributions: list[Contribution]
    tax_plan: TaxPlan | None = None
    social_security: SocialCase | None = None
    social_work_plan: WorkPolicy | None = None
    employment_plan: EmploymentPlan | None = None
    compensation_plan: CompensationPlan | None = None
    ira_plan: IRAPlan | None = None
    medicare_plan: MedicarePlan | None = None
    workplace_plan: WorkplacePlan | None = None
    hsa_plan: HSAPlan | None = None
    education_plan: EducationHouseholdPlan | None = None
    lot_plan: HouseholdLots | None = None
    sleeve_plan: SleevePlan | None = None
    exchange_fund_plan: ExchangeFundPlan | None = None
    option_plan: OptionPlan | None = None
    life_plan: LifeHouseholdPlan | None = None
    qoz_plan: QOZPlan | None = None
    advisory_fee_plan: AdvisoryPlan | None = None

    @model_validator(mode="after")
    def validate_inputs(self) -> Self:
        if self.social_work_plan is not None and self.social_security is None:
            raise ValueError("A work-test policy requires generated Social Security claims.")
        validate_dates(self)
        validate_references(self)
        validate_life_ownership(self)
        return self
