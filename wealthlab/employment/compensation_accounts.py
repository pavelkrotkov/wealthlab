"""Reconcile vested tranches to employer accounts without treating contingent grants as cash.

One account can contain multiple contractual vesting slices. Every modeled
employer account must reconcile, and ordinary household contributions cannot
bypass the tranche book and create an unmatched balance.
"""

from collections import defaultdict
from decimal import Decimal


def validate(scenario, accounts):
    opening = defaultdict(Decimal)
    owners = {m.id for m in scenario.members}
    for tranche in scenario.compensation_plan.tranches:
        account = accounts.get(tranche.account)
        validate_tranche(account, owners)
        opening[account.id] += tranche.opening_vested
    validate_balances(scenario, accounts, opening)


def validate_tranche(account, owners):
    if account is None or account.wrapper != "employer" or account.owner not in owners:
        raise ValueError("Each tranche requires an employer account with a known individual owner.")
    if account.currency != "USD":
        raise ValueError("This compensation layer requires USD-denominated employer accounts.")


def validate_balances(scenario, accounts, opening):
    employers = {a.id for a in scenario.accounts if a.wrapper == "employer"}
    if employers != set(opening):
        raise ValueError("Provide tranches for every employer account.")
    if any(accounts[key].balance != amount for key, amount in opening.items()):
        raise ValueError("Employer account balances must equal supplied vested tranche values.")
    if any(c.destination in opening for c in scenario.contributions):
        raise ValueError(
            "Employer grants must use tranche events, not household cash contributions."
        )
