"""Confirmed actual incoming plan cash, not a request or an ordinary IRA contribution."""

from datetime import date
from typing import Literal

from pydantic import model_validator

from wealthlab.household.records import Identifier, Money, Record


class IncomingIRARollover(Record):
    date: date
    owner: Identifier
    source: Identifier
    destination: Identifier
    amount: Money
    federal_basis_transferred: Money
    nj_basis_transferred: Money
    profile: Literal["ordinary_qualified_plan_cash_to_same_owner_traditional_ira"]
    eligible_direct_rollover_and_rmd_excluded_confirmed: bool
    independent_basis_and_no_special_features_confirmed: bool
    excluded_from_opening_balances_and_cash_receipts_confirmed: bool

    @model_validator(mode="after")
    def confirmed(self):
        if not all(
            (
                self.eligible_direct_rollover_and_rmd_excluded_confirmed,
                self.independent_basis_and_no_special_features_confirmed,
                self.excluded_from_opening_balances_and_cash_receipts_confirmed,
            )
        ):
            raise ValueError(
                "Confirm eligible incoming rollover, independent basis and no duplicate cash."
            )
        if max(self.federal_basis_transferred, self.nj_basis_transferred) > self.amount:
            raise ValueError(
                "This cash-rollover profile requires transferred basis no greater than value."
            )
        return self
