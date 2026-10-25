"""Reuse QuantLib's dated cash-flow solver; do not select among ambiguous IRRs.

Only one negative-to-positive sign transition after same-date aggregation is
accepted. More complex borrowing/premium patterns can have multiple roots, so
those inputs retain their dated cash ledger without a purported unique return.
"""

from collections import defaultdict
from decimal import Decimal
from itertools import pairwise
from math import expm1, isfinite

import QuantLib as ql


def calculate(flows):
    amounts = defaultdict(Decimal)
    for when, amount in flows:
        amounts[when] += amount
    ordered = sorted((when, amount) for when, amount in amounts.items() if amount)
    if not conventional(ordered):
        return dict(rate=None, status="no unique conventional cash-flow IRR")
    if any(not 1901 <= when.year <= 2199 for when, _ in ordered):
        return dict(rate=None, status="dates outside QuantLib range")
    return solve(ordered)


def solve(flows):
    leg = [ql.SimpleCashFlow(float(amount), ql.Date(d.day, d.month, d.year)) for d, amount in flows]
    when = flows[0][0]
    start = ql.Date(when.day, when.month, when.year)

    # Solve in continuous-rate space so bracketing never crosses an annual rate
    # of -100%. QuantLib supplies both dated NPV and the Brent root algorithm.
    def npv(continuous_rate):
        return ql.CashFlows.npv(
            leg,
            continuous_rate,
            ql.Actual365Fixed(),
            ql.Continuous,
            ql.Annual,
            True,
            start,
            start,
        )

    try:
        solver = ql.Brent()
        solver.setMaxEvaluations(10000)
        rate = expm1(solver.solve(npv, 1e-12, 0, 0.01))
    except (RuntimeError, OverflowError):
        return dict(rate=None, status="dated IRR solver did not converge")
    if not isfinite(rate) or rate <= -1:
        return dict(rate=None, status="no finite annual effective IRR")
    return dict(rate=rate, status="annual effective; actual/365 fixed")


def conventional(ordered):
    signs = [amount > 0 for _, amount in ordered]
    changes = sum(a != b for a, b in pairwise(signs))
    return bool(signs) and not signs[0] and signs[-1] and changes == 1
