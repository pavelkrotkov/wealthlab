"""Aggregate owner-level limits across destinations; only funded amounts consume them."""

from decimal import Decimal

from wealthlab.retirement.contribution_rules import (
    ira_limit,
    workplace_limits,
)
from wealthlab.retirement.ira_rules import phaseout, reduced


def allowed(case, person, order, used):
    if order.kind.endswith("ira"):
        cap = ira_limit(person, case)
        remaining = cap - used["traditional_ira"] - used["roth_ira"]
        if order.kind == "roth_ira":
            roth = reduced(cap, person.roth_ira_magi, phaseout(case, person, True))
            remaining = min(remaining, roth - used["roth_ira"])
        return max(Decimal(0), min(order.amount, remaining))
    total, pretax = workplace_limits(person, case)
    remaining = total - used["pretax_401k"] - used["roth_401k"]
    if order.kind == "pretax_401k":
        remaining = min(remaining, pretax - used["pretax_401k"])
    return max(Decimal(0), min(order.amount, remaining))
