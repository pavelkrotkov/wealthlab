"""Dated economic changes and supplied tax allocations are different events.

Vesting/forfeiture with amount=None affects the whole remaining value slice;
fixed dollar requests are capped by what remains. Cash elections do not alter
supplied taxable allocations in this conditional model.
"""

from datetime import date
from decimal import Decimal
from typing import Annotated, Literal

from pydantic import Field

from wealthlab.household.records import Identifier, Money, Record
from wealthlab.tax.facts import FederalIncome
from wealthlab.tax.nj_facts import NJIncome


class Event(Record):
    """Same-date operations use explicit sequence, never incidental input-list order."""

    date: date
    tranche: Identifier
    sequence: int = Field(ge=0, le=100000)


class Grant(Event):
    kind: Literal["grant"]
    amount: Money


class NetReturn(Event):
    kind: Literal["net_return"]
    rate: Annotated[Decimal, Field(ge=-1, le=10, max_digits=18, decimal_places=12)]


class Vest(Event):
    """None vests the entire remaining slice after its actual returns/forfeiture."""

    kind: Literal["vest"]
    amount: Money | None


class Forfeit(Event):
    kind: Literal["forfeit"]
    amount: Money | None


class Distribution(Event):
    kind: Literal["distribution"]
    amount: Money
    bucket: Literal["vested", "unvested"]
    purpose: Literal["ordinary", "tax_distribution"]
    election: Literal["cash", "retain"]


class Allocation(Event):
    """Already-allowed supplied tax amounts; economic value/cash do not change here."""

    kind: Literal["allocation"]
    federal: FederalIncome
    new_jersey: NJIncome


CompensationEvent = Annotated[
    Grant | NetReturn | Vest | Forfeit | Distribution | Allocation,
    Field(discriminator="kind"),
]
