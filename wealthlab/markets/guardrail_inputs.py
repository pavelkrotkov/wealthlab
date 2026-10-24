"""A bounded discretionary policy with explicit review frequency and hysteresis."""

from decimal import Decimal
from typing import Literal, Self

from pydantic import Field, model_validator

from wealthlab.household.records import Identifier
from wealthlab.tax.facts import TaxModel


class SpendingGuardrail(TaxModel):
    expense_ids: list[Identifier] = Field(min_length=1)
    review_interval_months: Literal[1, 3, 12] = 12
    trigger_real_wealth_drawdown: Decimal = Field(gt=0, lt=1)
    restore_real_wealth_drawdown: Decimal = Field(ge=0, lt=1)
    discretionary_cut_fraction: Decimal = Field(gt=0, lt=1)
    spending_floor_fraction: Decimal = Field(gt=0, le=1)
    wealth_includes_spending_effects_confirmed: bool

    @model_validator(mode="after")
    def limits(self) -> Self:
        if self.restore_real_wealth_drawdown >= self.trigger_real_wealth_drawdown:
            raise ValueError("Restore drawdown must be below the cut trigger.")
        if 1 - self.discretionary_cut_fraction < self.spending_floor_fraction:
            raise ValueError("The cut cannot violate the configured discretionary spending floor.")
        if len(self.expense_ids) != len(set(self.expense_ids)):
            raise ValueError("Guardrail expense IDs must be unique.")
        return self
