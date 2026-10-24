"""A dated trade has one explicit selection rule and no implicit financing."""

from datetime import date
from typing import Literal, Self

from pydantic import Field, model_validator

from wealthlab.household.records import Money, Record
from wealthlab.portfolio.models import Price, Quantity


class Trade(Record):
    date: date
    action: Literal["buy", "sell"]
    account_id: str
    security_id: str
    quantity: Quantity
    price: Price
    commission: Money
    selection: Literal["fifo", "hifo", "specific"] = "fifo"
    lot_ids: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def selected_ids(self) -> Self:
        if len(self.lot_ids) != len(set(self.lot_ids)):
            raise ValueError("Specific lot IDs must be unique.")
        if (self.selection == "specific") != bool(self.lot_ids):
            raise ValueError("Supply ordered lot IDs exactly when selection is specific.")
        if self.action == "buy" and self.selection != "fifo":
            raise ValueError("Lot selection applies only to sales.")
        return self
