"""Positive-net-income credit limitation with separately auditable paid tax and source bases.

PR Schedule C is recomputed for regular tax and ABT; prior/exempt foreign income
reduces the eligible paid amount. Payroll is never an income-tax credit input.
"""

from decimal import Decimal

from wealthlab.household.calendar import money


def limited(tax, paid, foreign_net, total_net, *, excluded_foreign_net=Decimal(0), paid_net=None):
    total_paid_net = total_net if paid_net is None else paid_net
    eligible = scaled_paid(paid, excluded_foreign_net, total_paid_net)
    fraction = (
        min(Decimal(1), max(Decimal(0), foreign_net) / total_net) if total_net > 0 else Decimal(0)
    )
    limit = money(tax * fraction)
    allowed = min(eligible, limit)
    return dict(
        tax_before_credit=tax,
        reported_paid_or_accrued=paid,
        paid_tax_reduction=paid - eligible,
        eligible_paid_tax=eligible,
        foreign_net_income=foreign_net,
        total_net_income=total_net,
        limitation_fraction=fraction,
        limitation=limit,
        allowed=allowed,
        unused_eligible=eligible - allowed,
    )


def scaled_paid(paid, excluded, paid_net):
    if paid_net <= 0:
        return Decimal(0)
    fraction = min(Decimal(1), max(Decimal(0), excluded) / paid_net)
    return money(paid * (1 - fraction))
