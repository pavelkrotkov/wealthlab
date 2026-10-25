"""Contractual release, blocked requests and conditional early cash exits remain distinct."""

from wealthlab.household.calendar import money
from wealthlab.products import exchange_fund_lots as lots
from wealthlab.products.conditional_allocations import events as allocations
from wealthlab.products.exchange_fund_basket import create_basket
from wealthlab.products.exchange_fund_trades import sell


def requested(ledger, request, prices, wallet, row):
    if request.action == "redeem" and ledger.active:
        if request.date < ledger.plan.liquid_after:
            return early(ledger, request, wallet, row)
        return release(ledger, request.date, prices, wallet, row)
    if request.action == "sell_liquid":
        return [sell(ledger.book, ledger.plan, prices, request.date, request.id)]
    return []


def early(ledger, request, wallet, row):
    """Only a full cash exit is modeled; supplied income does not become a second receipt.

    This requires explicit tax/basis confirmation because early partnership exits
    can trigger contributed-property and marketable-security rules independently.
    """
    if ledger.plan.early_redemption == "denied":
        row["denied_redemptions"] += 1
        return []
    if not request.early_tax_confirmed:
        raise ValueError("Confirm complete request-specific early-redemption tax recognition.")
    fee = money(ledger.nav * ledger.plan.early_fee_fraction)
    row["fees"] += fee
    row["early_cash"] = ledger.nav - fee
    wallet.deposit(row["early_cash"])
    ledger.nav = lots.ZERO
    ledger.active = False
    ledger.bases = dict.fromkeys(ledger.bases, lots.ZERO)
    return list(allocations(request.early_tax))


def release(ledger, when, prices, wallet, row):
    plan = ledger.plan
    federal = (
        max(lots.ZERO, ledger.nav - ledger.bases["federal"])
        if (plan.federal_basket_distribution == "denied")
        else lots.ZERO
    )
    nj = (
        max(lots.ZERO, ledger.nav - ledger.bases["nj"])
        if (plan.nj_basket_distribution == "denied")
        else lots.ZERO
    )
    ledger.bases["federal"] += federal
    ledger.bases["nj"] += nj
    row["basket_cash"] = create_basket(ledger.book, plan, ledger.nav, ledger.bases, prices, when)
    wallet.deposit(row["basket_cash"])
    ledger.nav = lots.ZERO
    ledger.active = False
    ledger.bases = dict.fromkeys(ledger.bases, lots.ZERO)
    return [lots.event(when, federal, nj, plan.federal_distribution_character)]
