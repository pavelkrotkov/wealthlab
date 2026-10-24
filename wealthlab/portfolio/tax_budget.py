"""Bounded search for the largest evaluated sale within a cumulative annual tax budget.

Credits, loss lots and bracket transitions can make tax impact nonmonotone. The
search checks a grid and refines above its largest feasible point; it does not
claim a global optimum or anticipate future market returns and purchases.
"""

from copy import deepcopy
from decimal import ROUND_DOWN, Decimal

from wealthlab.household.calendar import money
from wealthlab.portfolio.fund_distribution_limits import validate_fund_losses
from wealthlab.portfolio.nj_recognition import finish as finish_nj
from wealthlab.portfolio.policy_order import sale
from wealthlab.portfolio.tax_reporting import report

UNIT = Decimal("0.000001")


def impact(case, book, when):
    trial = deepcopy(book)
    validate_fund_losses(case, trial)
    trial.wash.finish(trial, when)
    finish_nj(case, trial, when)
    rows = report(case, trial, through_year=when.year, as_of=when)
    return rows[-1]["incremental_liability"]


def choose(case, book, policy, lots):
    total = sum((lot.quantity for lot in lots), Decimal(0))
    grid = sorted(
        {
            (total * index / policy.budget_grid_points).quantize(UNIT, rounding=ROUND_DOWN)
            for index in range(policy.budget_grid_points + 1)
        }
    )
    budget = policy.tax_budget
    assert budget is not None

    def feasible(quantity):
        if quantity and money(quantity * policy.prices[policy.security_id]) < policy.commission:
            return False
        trial = deepcopy(book)
        if quantity:
            trial.trade(sale(policy, quantity, lots))
        return impact(case, trial, policy.date) <= budget

    return largest_feasible(grid, feasible)


def largest_feasible(grid, feasible):
    accepted = [quantity for quantity in grid if feasible(quantity)]
    if not accepted:
        return Decimal(0)
    best = max(accepted)
    higher = [quantity for quantity in grid if quantity > best]
    return refine(best, min(higher), feasible) if higher else best


def refine(low, high, feasible):
    """Keep a feasible lower endpoint; stop at the model's microshare resolution."""
    for _ in range(24):
        middle = ((low + high) / 2).quantize(UNIT, rounding=ROUND_DOWN)
        if middle == low:
            break
        if feasible(middle):
            low = middle
        else:
            high = middle
    return low


def diagnostics(case, book, policy):
    value = impact(case, book, policy.date)
    return dict(
        tax_budget=policy.tax_budget,
        estimated_incremental_liability=value,
        budget_met=value <= policy.tax_budget,
        search_scope=(
            "Largest evaluated feasible sale; annual forecast at decision date, "
            "not a global optimum"
        ),
    )
