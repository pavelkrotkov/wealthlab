"""Cross-record validation before inputs can reach the projection engine."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from wealthlab.household.scenario import Scenario

from wealthlab.household.relationships import (
    validate_currencies,
    validate_owners,
    validate_transfers,
)

TABLES = ("members", "accounts", "incomes", "expenses", "debts", "contributions")


def validate_dates(scenario: "Scenario") -> None:
    if not scenario.start < scenario.end:
        raise ValueError("Projection end is exclusive and must follow its start.")
    if (scenario.end - scenario.start).days > 120 * 366:
        raise ValueError("Projection cannot exceed 120 years.")
    for member in scenario.members:
        age = (scenario.start - member.birth_date).days / 365.25
        if not 0 < age <= 120:
            raise ValueError("Members must be born and no older than 120 at projection start.")
    if scenario.usd_per_currency.get("USD") != 1:
        raise ValueError("USD exchange rate must be exactly 1.")


def validate_references(scenario: "Scenario") -> None:
    records = [record for key in TABLES for record in getattr(scenario, key)]
    identifiers = [record.id for record in records]
    if len(set(identifiers)) != len(identifiers):
        raise ValueError("Record identifiers must be globally unique.")
    validate_owners(scenario)
    validate_currencies(scenario, records)
    validate_transfers(scenario)


def validate_resolved(scenario):
    unresolved = [
        record.id
        for table in TABLES
        for record in getattr(scenario, table)
        if record.provenance == "unresolved"
    ]
    if unresolved:
        raise ValueError("Resolve critical inputs before projecting: " + ", ".join(unresolved))
