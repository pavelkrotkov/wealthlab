"""Fund spending and withdrawal-induced taxes from explicitly available liquid assets."""

from collections.abc import Callable
from decimal import Decimal

from wealthlab.household.calendar import money


def solve(
    cash: Decimal,
    spending: Decimal,
    liquid_assets: Decimal,
    tax_balance: Callable[[Decimal], Decimal],
) -> dict:
    """Monotone withdrawal iteration; a feasible funding amount, not an optimum.

    The callback evaluates the total unpaid tax after a proposed withdrawal,
    without mutating holdings. Refunds remain receivable and cannot finance this
    payment date. Tax cliffs may cause over-withdrawal; comparison reports the
    actual amount and leftover cash rather than claiming the minimum withdrawal.
    """
    if any(not value.is_finite() or value < 0 for value in (cash, spending, liquid_assets)):
        raise ValueError("Cash, spending and available assets must be finite and nonnegative.")
    withdrawal = Decimal(0)
    for iteration in range(1, 101):
        balance = tax_balance(withdrawal)
        if not balance.is_finite():
            raise ValueError("Tax callback returned a non-finite balance.")
        balance = money(balance)
        needed = max(Decimal(0), spending + max(Decimal(0), balance) - cash - withdrawal)
        if needed == 0 or withdrawal == liquid_assets:
            return outcome(cash, spending, withdrawal, balance, iteration, True)
        withdrawal = min(liquid_assets, withdrawal + money(needed))
    return outcome(cash, spending, withdrawal, tax_balance(withdrawal), 100, False)


def outcome(cash, spending, withdrawal, balance, iterations, converged) -> dict:
    available = cash + withdrawal
    tax_paid = min(available, max(Decimal(0), balance))
    spending_paid = min(spending, available - tax_paid)
    return dict(
        withdrawal=withdrawal,
        tax_balance=balance,
        tax_paid=tax_paid,
        spending_paid=spending_paid,
        cash_left=available - tax_paid - spending_paid,
        tax_unpaid=max(Decimal(0), balance - tax_paid),
        spending_shortfall=spending - spending_paid,
        refund_receivable=max(Decimal(0), -balance),
        iterations=iterations,
        converged=converged,
    )
