"""Complete designated Roth plan contracts retain independent federal/state cost histories."""

from datetime import date
from typing import Literal

from pydantic import Field

from wealthlab.household.records import Identifier, Money
from wealthlab.retirement.workplace_withdrawal_inputs import WorkplaceCashOrder
from wealthlab.tax.facts import TaxModel


class RothContract(TaxModel):
    sources: list[Identifier] = Field(min_length=1)
    separation_date: date
    first_federal_contribution_year: int | None = Field(default=None, ge=2006, le=2200)
    federal_basis: Money
    nj_basis: Money
    complete_vested_ordinary_designated_roth_contract_confirmed: bool
    no_inplan_conversions_inherited_loans_nua_or_other_special_history_confirmed: bool
    complete_cash_events_excluded_from_other_inputs_confirmed: bool
    nj_treatment: Literal["conditional_same_qualification_and_pro_rata_cost"]
    independent_nj_basis_and_conditional_treatment_confirmed: bool


class WorkplaceRothCashPlan(TaxModel):
    contracts: dict[Identifier, RothContract] = Field(min_length=1)
    orders: list[WorkplaceCashOrder] = Field(default_factory=list)
    timing: Literal["first_day_before_employee_deferrals_and_month_end_returns"]
    rule_mode: Literal["frozen_2026_ordinary_designated_roth_cash"]
