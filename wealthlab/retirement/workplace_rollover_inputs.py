"""A direct-transfer request is funded from actual eligible separated plan assets."""

from datetime import date

from pydantic import model_validator

from wealthlab.household.records import Identifier, Money, Record


class WorkplaceRolloverOrder(Record):
    date: date
    source: Identifier
    destination: Identifier
    amount: Money
    eligible_direct_cash_rollover_to_same_owner_ordinary_ira_confirmed: bool

    @model_validator(mode="after")
    def confirmed(self):
        if not self.eligible_direct_cash_rollover_to_same_owner_ordinary_ira_confirmed:
            raise ValueError("Confirm eligible direct cash rollover to a same-owner ordinary IRA.")
        return self
