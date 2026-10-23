"""Select currently liquid loss lots without using closing marks or future purchases.

Thresholds compare allocated federal basis with marked sale proceeds before fees.
The gross-dollar cap constrains sold units, not replacement purchases or tax savings.
Re-read eligible lots after each pair because wash matching can split later holdings.
"""

from datetime import date, timedelta
from decimal import ROUND_DOWN, Decimal

from wealthlab.household.calendar import money
from wealthlab.portfolio.lot_parts import split
from wealthlab.portfolio.orders import Trade
from wealthlab.portfolio.selection import candidates


def lots(book, policy):
    probe = Trade(
        id=policy.id,
        provenance=policy.provenance,
        date=policy.date,
        action="sell",
        account_id=policy.account_id,
        security_id=policy.security_id,
        quantity=Decimal(1),
        price=policy.prices[policy.security_id],
        commission=policy.commission_per_trade,
        selection=policy.selection,
    )
    return candidates(book.lots, probe)


def replacement_blocked(book, policy):
    """Avoid repurchasing a recently sold loss group; future manual orders remain unknown."""
    group = book.securities[policy.replacement_id].wash_group
    for row in book.disposals:
        sold = date.fromisoformat(row["date"])
        same = book.securities[row["security_id"]].wash_group == group
        if (
            same
            and row["federal_gross_gain"] < 0
            and sold <= policy.date <= sold + timedelta(days=30)
        ):
            return True
    return False


def quantity(lot, policy, remaining):
    price = policy.prices[policy.security_id]
    available = lot.quantity if remaining is None else min(lot.quantity, remaining / price)
    qty = available.quantize(Decimal("0.000001"), rounding=ROUND_DOWN)
    taken, _ = split(lot, qty)
    loss = taken.federal_basis - money(qty * price)
    threshold = max(policy.minimum_loss, taken.federal_basis * policy.minimum_loss_fraction)
    return qty if loss > 0 and loss >= threshold else Decimal(0)


def next_lot(book, policy, seen):
    """Wash adjustments may split later lots; observe the current ledger after each pair."""
    return next((lot for lot in lots(book, policy) if lot.id not in seen), None)
