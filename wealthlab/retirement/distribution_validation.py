"""Every configured account is an ordinary, non-inherited traditional or Roth IRA."""

from datetime import date

from wealthlab.retirement.account_liquidity import validate as validate_liquidity
from wealthlab.retirement.distribution_owner_validation import validate_owners, validate_tax
from wealthlab.retirement.ira_contribution_validation import validate as validate_contributions


def validate(case):
    if not case.opening_context_complete:
        raise ValueError("Confirm complete IRA pools/history and no unsupported opening events.")
    people = {person.id: person for person in case.owners}
    accounts = {account.id: account for account in case.accounts}
    validate_liquidity(
        case.liquidity_locks, accounts, date(case.year, 1, 1), date(case.year + 1, 1, 1)
    )
    validate_records(case)
    validate_owners(case)
    validate_accounts(case, people)
    for item in [*case.orders, *case.returns]:
        if item.date.year != case.year:
            raise ValueError("Distribution events must fall within the selected year.")
    validate_orders(case, accounts)
    validate_returns(case, accounts)
    validate_tax(case)
    validate_contributions(case)


def validate_accounts(case, people):
    for account in case.accounts:
        validate_account(account, people)


def validate_account(account, people):
    """Only explicit ordinary IRA holdings belong in these aggregated pools.

    Generic household wrapper names cannot establish IRA status. The user must
    map workplace, inherited and annuity contracts outside this annual layer.
    Fees and foreign currency require their own cash and recognition adapters.
    """
    if account.owner not in people or account.currency != "USD" or account.monthly_fee:
        raise ValueError("Use known owners and USD IRA accounts without monthly fees here.")
    expected = account.product.removesuffix("_ira")
    if account.wrapper != expected:
        raise ValueError("This distribution layer supports ordinary traditional/Roth IRAs only.")
    if (
        account.wrapper == "roth"
        and account.balance
        and people[account.owner].roth_first_year is None
    ):
        raise ValueError("An existing Roth balance requires its first contribution year.")


def validate_orders(case, accounts):
    for order in case.orders:
        source = accounts.get(order.source)
        if source is None:
            raise ValueError("Unknown distribution source account.")
        if order.kind == "withdrawal":
            if order.destination is not None:
                raise ValueError("Withdrawals go to cash; only conversions have a destination IRA.")
        else:
            validate_conversion(order, source, accounts)


def validate_conversion(order, source, accounts):
    """A conversion is a same-owner transfer, never spendable cash.

    A full funded conversion is not itself an early distribution subject to the
    ten-percent additional tax; later withdrawal of its taxable bucket can be.
    """
    target = accounts.get(order.destination)
    if source.wrapper != "traditional" or target is None or target.wrapper != "roth":
        raise ValueError("Conversions transfer traditional IRA assets to a Roth IRA.")
    if target.owner != source.owner or order.early_penalty_exception:
        raise ValueError("Conversions keep the same owner and do not use withdrawal exceptions.")


def validate_returns(case, accounts):
    if any(item.account_id not in accounts for item in case.returns):
        raise ValueError("Unknown account in a dated return assumption.")


def validate_records(case):
    """Unknown eligibility blocks the entire run before it can change any balance."""
    records = [*case.owners, *case.accounts, *case.orders, *case.returns, *case.liquidity_locks]
    ids = [item.id for item in records]
    if len(ids) != len(set(ids)):
        raise ValueError("Distribution case IDs must be unique across all tables.")
    if any(item.provenance == "unresolved" for item in records):
        raise ValueError("Resolve distribution assumptions before calculating.")
