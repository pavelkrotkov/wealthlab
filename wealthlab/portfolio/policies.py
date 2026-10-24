"""Dated sale decisions consume only their explicitly supplied current price snapshot."""

from datetime import date
from decimal import Decimal
from typing import Literal, Self

from pydantic import Field, model_validator

from wealthlab.household.records import Money, Record
from wealthlab.portfolio.models import Price


class SalePolicy(Record):
    date: date
    account_id: str
    security_id: str
    mode: Literal["retain", "sell_all", "original_fraction", "target_weight", "tax_budget"]
    tax_budget: Money | None = None
    budget_grid_points: int = Field(default=32, ge=2, le=128)
    fraction: Decimal | None = Field(default=None, ge=0, le=1)
    prices: dict[str, Price]
    commission: Money = Decimal(0)
    selection: Literal["fifo", "hifo"] = "fifo"

    @model_validator(mode="after")
    def target(self) -> Self:
        needs_target = self.mode in {"original_fraction", "target_weight"}
        if needs_target != (self.fraction is not None):
            raise ValueError("Supply fraction exactly for original_fraction or target_weight.")
        if (self.mode == "tax_budget") != (self.tax_budget is not None):
            raise ValueError("Supply tax_budget exactly for tax_budget policies.")
        return self
