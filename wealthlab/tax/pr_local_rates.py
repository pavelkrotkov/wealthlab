"""Published 2025 PR regular/ABT schedules and statutory gradual adjustment.

Code 1021.01(b)(5)(E) caps the adjustment at $8,895 plus 33% of personal
and dependent exemptions. Code 1021.02's ABT bands apply to the whole base.
"""

from decimal import Decimal

from wealthlab.household.calendar import money

D = Decimal
REGULAR = (
    (D(0), D(0), D(0)),
    (D(9000), D(0), D(".07")),
    (D(25000), D(1120), D(".14")),
    (D(41500), D(3430), D(".25")),
    (D(61500), D(8430), D(".33")),
)
ABT = ((250000, ".24"), (150000, ".10"), (75000, ".05"), (50000, ".03"), (25000, ".01"))


def bracket(net):
    for threshold, base, rate in reversed(REGULAR):
        if net >= threshold:
            return money(base + (net - threshold) * rate)
    return D(0)


def gradual(net, exemptions):
    return money(min(D(".05") * max(D(0), net - 500000), D(8895) + D(".33") * exemptions))


def regular(net, exemptions, reduction_gross):
    factor = D(".92") if reduction_gross <= 100000 else D(".95")
    adjustment = gradual(net, exemptions)
    return dict(
        bracket_tax=bracket(net),
        gradual_adjustment=adjustment,
        reduction_factor=factor,
        tax=money((bracket(net) + adjustment) * factor),
    )


def abt(net, *, wage_only=False):
    if wage_only:
        return D(0)
    for threshold, rate in ABT:
        if net > threshold:
            return money(net * D(rate))
    return D(0)
