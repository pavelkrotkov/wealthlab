"""Confirmed qualifying salary reductions use the current month's pooled W2 payroll."""

from datetime import date
from typing import Literal

from pydantic import Field

from wealthlab.household.records import Identifier, Money, Record
from wealthlab.tax.facts import TaxModel


class HSAPayrollOrder(Record):
    date: date
    owner: Identifier
    destination: Identifier
    amount: Money


class HSAPayrollPlan(TaxModel):
    orders: list[HSAPayrollOrder] = Field(default_factory=list)
    qualifying_section125_w2_employee_confirmed: bool
    gross_wages_before_salary_reduction_confirmed: bool
    complete_elections_and_no_other_payroll_reductions_confirmed: bool
    nj_salary_reduction_treatment: Literal["taxable_wages_assumption"]
    timing: Literal["monthly_after_employee_401k_before_other_hsa_events"]
