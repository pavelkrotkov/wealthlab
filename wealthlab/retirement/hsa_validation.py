"""Reject missing coverage months, ambiguous receipts and unsupported account types."""

from datetime import date

from wealthlab.retirement.contribution_assumptions import rule_year
from wealthlab.retirement.hsa_receipts import validate_receipt
from wealthlab.retirement.hsa_shares import validate_shares


def validate(case):
    rule_year(case)
    if not case.complete_context:
        raise ValueError("Confirm complete HSA contributions, coverage and receipt history.")
    owners = {owner.id: owner for owner in case.owners}
    accounts = {account.id: account for account in case.accounts}
    records = [
        *case.owners,
        *case.accounts,
        *case.cash_receipts,
        *case.medical_receipts,
        *case.contributions,
        *case.withdrawals,
        *case.interest,
    ]
    validate_records(records)
    if case.married and len(owners) != 2:
        raise ValueError("List both spouses and their coverage when applying married HSA limits.")
    validate_owners(case)
    for account in accounts.values():
        validate_account(case, account, owners)
    validate_shares(case)
    validate_events(case, accounts, owners)


def validate_records(records):
    ids = [item.id for item in records]
    if len(ids) != len(set(ids)):
        raise ValueError("HSA IDs must be unique across every table.")
    if any(item.provenance == "unresolved" for item in records):
        raise ValueError("Resolve critical HSA assumptions before calculating.")


def validate_account(case, account, owners):
    """Opening balances are January-first cash already in an existing HSA.

    A newly established current-year account may start empty; current-year
    deposits belong in the dated contribution ledger rather than opening cash.
    """
    if account.owner not in owners or account.wrapper != "hsa":
        raise ValueError("Use HSA accounts with known owners.")
    if account.currency != "USD" or account.monthly_fee:
        raise ValueError("The HSA cash layer requires USD accounts without monthly fees.")
    if account.balance and owners[account.owner].established.year > case.year - 1:
        raise ValueError("A positive opening HSA balance must be established before the year.")


def validate_events(case, accounts, owners):
    """Annual contribution capacity does not override cash-event chronology.

    A contribution may occur after eligibility ends, using earned annual room,
    but no cash event can precede actual HSA establishment.
    """
    collections = [case.cash_receipts, case.contributions, case.withdrawals, case.interest]
    for collection in collections:
        if any(item.date.year != case.year for item in collection):
            raise ValueError("HSA cash events must fall within the selected year.")
    for item in case.contributions:
        validate_destination(item.destination, item.date, accounts, owners)
    for item in case.interest:
        validate_destination(item.account_id, item.date, accounts, owners)
    validate_withdrawals(case, accounts, owners)


def validate_withdrawals(case, accounts, owners):
    receipts = {item.id: item for item in case.medical_receipts}
    for item in case.withdrawals:
        validate_destination(item.source, item.date, accounts, owners)
        if (
            len(set(item.receipt_ids)) != len(item.receipt_ids)
            or set(item.receipt_ids) - receipts.keys()
        ):
            raise ValueError("Withdrawal receipt IDs must be known and unique.")
    for receipt in receipts.values():
        validate_receipt(receipt, owners)


def validate_destination(identity, when, accounts, owners):
    if identity not in accounts:
        raise ValueError("Unknown HSA account in cash event.")
    if when < owners[accounts[identity].owner].established:
        raise ValueError("HSA cash events cannot precede establishment.")


def validate_owners(case):
    for owner in case.owners:
        validate_owner_dates(owner, case.year)
        if {month.month for month in owner.months} != set(range(1, 13)):
            raise ValueError("Supply each owner's twelve distinct HSA eligibility months.")


def validate_owner_dates(owner, year):
    if owner.birth_date > date(year, 1, 1) or owner.established < owner.birth_date:
        raise ValueError("HSA birth/establishment dates contradict the modeled year.")
    if owner.established > date(year, 12, 31):
        raise ValueError("An HSA cannot be established after this modeled year.")
    if owner.disabled_since is not None and owner.disabled_since < owner.birth_date:
        raise ValueError("Disability cannot precede the owner's birth.")
