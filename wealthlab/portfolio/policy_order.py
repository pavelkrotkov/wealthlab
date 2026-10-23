"""Build the same specifically identified sale for policy trials and actual execution."""

from wealthlab.portfolio.orders import Trade


def sale(policy, quantity, lots):
    return Trade(
        id=policy.id,
        provenance=policy.provenance,
        date=policy.date,
        action="sell",
        account_id=policy.account_id,
        security_id=policy.security_id,
        quantity=quantity,
        price=policy.prices[policy.security_id],
        commission=policy.commission,
        selection="specific",
        lot_ids=[lot.id for lot in lots],
    )
