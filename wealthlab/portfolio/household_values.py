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
