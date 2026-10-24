"""Conditional net employer factors and an observed-price employment trigger.

A linked job loss is a supplied scenario rule, never an estimated probability.
It starts next month, so an observed decline cannot erase already-earned wages.
"""

from decimal import Decimal
from typing import Annotated, Literal

from pydantic import Field

from wealthlab.household.records import Identifier
from wealthlab.tax.facts import TaxModel


class EmploymentLink(TaxModel):
    path_id: Identifier
    drawdown_trigger: Annotated[Decimal, Field(gt=0, le=1)]
    months_out: int = Field(ge=1, le=1200)
    return_multiplier: Annotated[Decimal, Field(gt=0, le=10, decimal_places=6)]
    forfeit_remaining_unvested: bool
    replace_future_work_changes_confirmed: bool


class EmployerBinding(TaxModel):
    account_id: Identifier
    factor: Identifier
    return_convention: Literal["net_mark_return_no_separate_cash_yield"]
    replace_entered_net_returns_confirmed: bool
    event_sequence_start: int = Field(ge=0, le=99000)
    employment: EmploymentLink | None = None
