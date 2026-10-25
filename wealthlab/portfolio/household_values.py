"""One marked account value serves opening validation and the actual wallet sync."""

from decimal import Decimal

from wealthlab.household.calendar import money


def account_value(lots, identity, cash, prices):
    return money(
        cash
        + sum(
            (lot.quantity * prices[lot.security_id] for lot in lots if lot.account_id == identity),
            Decimal(0),
        )
    )


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
