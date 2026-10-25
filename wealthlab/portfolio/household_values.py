"""One marked account value serves opening validation and the actual wallet sync."""

from decimal import Decimal

from wealthlab.household.calendar import money


def account_value(lots, identity, cash, prices):
    return money(unrounded_account_value(lots, identity, cash, prices))


def unrounded_account_value(lots, identity, cash, prices):
    return cash + sum(
        (lot.quantity * prices[lot.security_id] for lot in lots if lot.account_id == identity),
        Decimal(0),
    )


def rounding_residual(book, prices):
    """Bridge per-account cent marks to the raw marks used in issuer exposure.

    This changes only an exposure denominator. Actual cash and household wealth
    remain on their existing cent-settled ledger, including cash and receivables.
    """
    raw = [
        unrounded_account_value(book.lots.values(), identity, cash, prices)
        for identity, cash in book.cash.items()
    ]
    return sum((amount - money(amount) for amount in raw), Decimal(0))


def security_values(book, prices):
    return {
        security: sum(
            (
                lot.quantity * prices[security]
                for lot in book.lots.values()
                if lot.security_id == security
            ),
            Decimal(0),
        )
        for security in book.securities
    }
