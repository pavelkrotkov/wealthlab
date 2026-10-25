"""Explicit factor mappings and frozen option-pricing assumptions, never quote history."""

from pydantic import Field

from wealthlab.household.records import Identifier
from wealthlab.tax.facts import TaxModel


class OptionBinding(TaxModel):
    account_id: Identifier
    stock_factor: Identifier
    index_factor: Identifier
    rate: float = Field(ge=-0.1, le=1)
    stock_vol: float = Field(gt=0, le=5)
    index_vol: float = Field(gt=0, le=5)
    stock_yield: float = Field(ge=0, le=1)
    index_yield: float = Field(ge=0, le=1)
    replace_dated_marks_confirmed: bool
    hypothetical_model_execution_confirmed: bool
