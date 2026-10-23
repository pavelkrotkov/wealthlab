"""Sale proceeds fund existing fee debt, commissions, then replacement purchases.

No outside cash is assumed. Paying an old fee is not a second expense; the fee
ledger already included its obligation in pre-tax wealth before the sale.
"""

from decimal import ROUND_DOWN, Decimal

from wealthlab.household.calendar import money
from wealthlab.portfolio.generated_orders import identity
from wealthlab.portfolio.orders import Trade


def pair(book, policy, lot, quantity, index):
    fee = policy.commission_per_trade
    gross = money(quantity * policy.prices[policy.security_id])
    net = gross - 2 * fee - book.fee_owed[policy.account_id]
    if net <= 0:
        return None
    replacement_quantity = (net / policy.prices[policy.replacement_id]).quantize(
        Decimal("0.000001"), rounding=ROUND_DOWN
    )
    if not replacement_quantity:
        return None
    common = dict(
        provenance=policy.provenance, date=policy.date, account_id=policy.account_id, commission=fee
    )
    sale = Trade(
        **common,
        id=identity(book, policy.id, f"sell_{index}"),
        action="sell",
        security_id=policy.security_id,
        quantity=quantity,
        price=policy.prices[policy.security_id],
        selection="specific",
        lot_ids=[lot.id],
    )
    purchase = Trade(
        **common,
        id=identity(book, policy.id, f"buy_{index}"),
        action="buy",
        security_id=policy.replacement_id,
        quantity=replacement_quantity,
        price=policy.prices[policy.replacement_id],
    )
    return sale, purchase
