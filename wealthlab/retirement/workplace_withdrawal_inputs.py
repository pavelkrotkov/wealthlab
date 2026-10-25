"""Explicit ordinary 401(k) cash withdrawals; no inferred plan permission or basis."""

from datetime import date
from decimal import Decimal
from typing import Annotated, Literal

from pydantic import Field, model_validator

from wealthlab.household.records import Identifier, Money, Record
from wealthlab.retirement.workplace_rmd_inputs import WorkplaceRMDPlan
from wealthlab.tax.facts import TaxModel

Rate = Annotated[Decimal, Field(ge=0, le=1, max_digits=12, decimal_places=10)]


class CashProfile(TaxModel):
    separation_date: date
    eligible_nonperiodic_cash_distributions_confirmed: bool
    fully_vested_zero_federal_and_nj_basis_confirmed: bool
    no_inherited_loans_nua_hardship_or_other_special_features_confirmed: bool
    complete_distributions_excluded_from_other_inputs_confirmed: bool
    birth_1959_start_age: Literal[73, 75] | None = None


class WorkplaceCashOrder(Record):
    date: date
    source: Identifier
    amount: Money
    federal_withholding_rate: Annotated[Decimal, Field(ge=Decimal(".20"), le=1)] = Decimal(".20")
    nj_withholding_rate: Rate = Decimal(0)

    @model_validator(mode="after")
    def rates(self):
        if self.federal_withholding_rate + self.nj_withholding_rate > 1:
            raise ValueError("Combined source withholding rates cannot exceed gross cash.")
        return self


class WorkplaceCashPlan(TaxModel):
    profiles: dict[Identifier, CashProfile] = Field(min_length=1)
    orders: list[WorkplaceCashOrder] = Field(default_factory=list)
    rmd: WorkplaceRMDPlan | None = None
    timing: Literal["first_day_before_employee_deferrals_and_month_end_returns"]
