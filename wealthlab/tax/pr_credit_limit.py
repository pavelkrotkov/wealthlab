"""Positive-net-income credit limitation with separately auditable paid tax and source bases.

PR Schedule C is recomputed for regular tax and ABT; prior/exempt foreign income
reduces the eligible paid amount. Payroll is never an income-tax credit input.
"""

from decimal import Decimal

from wealthlab.household.calendar import money
from wealthlab.tax.pr_credit_allocation import fraction, percentage


def limited(tax, paid, foreign_net, total_net, *, excluded_foreign_net=Decimal(0), paid_net=None):
    total_paid_net = total_net if paid_net is None else paid_net
    eligible = scaled_paid(paid, excluded_foreign_net, total_paid_net)
    total_fraction = fraction(foreign_net, total_net)
    country_fraction = percentage(foreign_net, total_net)
    limit = money(tax * country_fraction)
    total_limit = money(tax * total_fraction)
    allowed = min(eligible, limit, total_limit)
    return dict(
        tax_before_credit=tax,
        reported_paid_or_accrued=paid,
        paid_tax_reduction=paid - eligible,
        eligible_paid_tax=eligible,
        foreign_net_income=foreign_net,
        total_net_income=total_net,
        limitation_fraction=country_fraction,
        limitation=limit,
        total_limitation_fraction=total_fraction,
        total_limitation=total_limit,
        allowed=allowed,
        unused_eligible=eligible - allowed,
    )


def scaled_paid(paid, excluded, paid_net):
    if paid_net <= 0:
        return Decimal(0)
    fraction = min(Decimal(1), max(Decimal(0), excluded) / paid_net)
    return money(paid * (1 - fraction))
