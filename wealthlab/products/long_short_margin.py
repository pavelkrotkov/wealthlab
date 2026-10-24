"""Monthly maintenance is a supplied gross-exposure rule, not a broker requirement.

A loan survives insolvency and forced liquidation. Failure to post collateral
is visible even if a later unwind satisfies the remaining cash liability.
Market locks prevent a complete unwind and retain both legs and borrowings.
"""

from wealthlab.household.calendar import money
from wealthlab.products.long_short_book import ZERO, deposit, equity, gross
from wealthlab.products.long_short_trading import liquidate


def check(book, case, locked):
    if book["closed"]:
        return dict(
            margin_requested=ZERO,
            margin_topup=ZERO,
            margin_unfunded=ZERO,
            forced_liquidation=False,
            margin_exit_blocked=False,
        )
    needed = max(ZERO, money(gross(book) * case.maintenance_fraction_of_gross) - equity(book))
    paid = ZERO
    if needed and case.margin_policy == "top_up_then_liquidate":
        paid = min(needed, book["outside"])
        book["outside"] -= paid
        deposit(book, paid)
    shortfall = needed - paid
    audit = dict(
        margin_requested=needed,
        margin_topup=paid,
        margin_unfunded=shortfall,
        forced_liquidation=False,
        margin_exit_blocked=bool(shortfall and locked),
    )
    if shortfall and not locked:
        audit.update(liquidate(book, case.exit_cost), forced_liquidation=True)
    return audit
