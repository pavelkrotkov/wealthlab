"""Explicit outgoing-only scenario restrictions retain asset value and incoming deposits.

These are supplied liquidity assumptions, not legal restrictions inferred from
an account wrapper. Dates are inclusive/exclusive; annual compilation clips a
multi-year restriction to the selected year without extending the original interval.
"""

from datetime import date

from pydantic import model_validator

from wealthlab.household.records import Identifier, Record


class AccountLock(Record):
    account_id: Identifier
    start: date
    end: date

    @model_validator(mode="after")
    def ordered(self):
        if self.end <= self.start:
            raise ValueError("Account liquidity lock end must follow start.")
        return self


def blocked(locks, identity, when):
    return any(lock.account_id == identity and lock.start <= when < lock.end for lock in locks)


def validate(locks, accounts, start, end):
    if any(lock.account_id not in accounts for lock in locks):
        raise ValueError("Unknown account in outgoing liquidity restriction.")
    if any(lock.start < start or lock.end > end for lock in locks):
        raise ValueError("Account liquidity restrictions must lie inside the projection.")
    if any(lock.provenance == "unresolved" for lock in locks):
        raise ValueError("Resolve outgoing account liquidity assumptions before projecting.")


def annual(locks, year):
    start, end = date(year, 1, 1), date(year + 1, 1, 1)
    return [
        lock.model_copy(update=dict(start=max(start, lock.start), end=min(end, lock.end)))
        for lock in locks
        if lock.start < end and start < lock.end
    ]
