"""Validate ownership, currency mappings and internal transfer destinations."""

from typing import TYPE_CHECKING

from wealthlab.products.life_household_records import validate_ownership as validate_life_ownership

if TYPE_CHECKING:
    from wealthlab.household.scenario import Scenario


def validate_owners(scenario: "Scenario") -> None:
    members = {member.id for member in scenario.members}
    if "joint" in members:
        raise ValueError("The identifier joint is reserved for shared ownership.")
    for record in scenario.accounts + scenario.incomes:
        if record.owner not in members | {"joint"}:
            raise ValueError("Account and income owners must name a member or joint.")
    for income in scenario.incomes:
        if income.stop_at_retirement and income.owner not in members:
            raise ValueError("Retirement-linked income requires a specific member owner.")

    validate_life_ownership(scenario)


def validate_currencies(scenario: "Scenario", records: list) -> None:
    currencies = {record.currency for record in records if hasattr(record, "currency")}
    if not currencies <= scenario.usd_per_currency.keys():
        raise ValueError("Every currency needs an explicit USD exchange rate.")


def validate_transfers(scenario: "Scenario") -> None:
    cash = {account.id for account in scenario.accounts if account.wrapper == "cash"}
    targets = {account.id for account in scenario.accounts} - cash
    if not cash:
        raise ValueError("At least one cash account is required.")
    if any(item.destination not in targets for item in scenario.contributions):
        raise ValueError("Contribution destination must name a non-cash account.")
