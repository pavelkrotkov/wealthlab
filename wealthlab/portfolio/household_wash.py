"""Observed January trades finalize December losses in their original tax year.

Historical cash rows remain untouched. A dated revision records the corrected
return, its remaining payment position and fixed IRA election eligibility.
Terminal closure needs an explicit no-replacement assumption and credits only
a tax receivable; it cannot deposit an unreceived refund into spending cash.
"""

from datetime import date
from decimal import Decimal

from wealthlab.household.calendar import money
from wealthlab.portfolio.household_recognition import totals
from wealthlab.portfolio.household_wash_consumers import (
    check_ira,
    medicare_revision,
    update_education,
)
from wealthlab.portfolio.tax_recognition import gains, with_gains
from wealthlab.tax.annual import evaluate
from wealthlab.tax.return_reconciliation import revise


def bind(lots, taxes, ira, medicare, education):
    if lots is not None:
        lots.taxes, lots.ira, lots.medicare, lots.education = taxes, ira, medicare, education


def pending(lots, year):
    return any(
        r["date"].startswith(str(year)) and (r["federal_pending_loss"] or r["nj_pending_loss"])
        for r in lots.book.disposals
    )


def observe(lots):
    if lots.plan.year_end_wash_policy != "january_reconcile":
        return
    totals(lots.case, lots.book, lots.when)
    for year in sorted(lots.taxes.provisional_returns):
        if year < lots.when.year and not pending(lots, year):
            reconcile(lots, year, lots.when)


def reconcile(lots, year, when):
    federal, nj, _ = gains(lots.book, year)
    old_federal, old_nj = lots.reported[year]
    change = {k: v - old_federal[k] for k, v in federal.items()}
    original = lots.taxes.closed_returns[year].case
    annual = with_gains(original, change, nj - old_nj)
    result = evaluate(annual)
    checked = check_ira(lots.ira, year, annual, result)
    medicare = medicare_revision(lots.medicare, year, result, when)
    audit = revise(lots.taxes, year, annual, when)
    if medicare is not None:
        lots.medicare.case = medicare
    audit["ira_eligibility"] = checked
    update_education(lots.education, year, result)
    lots.taxes.provisional_returns.remove(year)
    lots.reported[year] = (federal, nj)
    lots.reconciliations.append(audit)


def finish(lots, rows):
    if not lots.taxes.provisional_returns:
        return
    if lots.plan.post_horizon_purchases != "none_for_30_days":
        raise ValueError(
            "Unfinalized tax returns require January observations or a no-replacement assumption."
        )
    year = max(lots.taxes.provisional_returns)
    when = date(year + 1, 1, 31)
    totals(lots.case, lots.book, when)
    for closed in sorted(lots.taxes.provisional_returns):
        reconcile(lots, closed, when)
    terminal_position(lots, rows[-1])


def terminal_position(lots, row):
    taxes = lots.taxes
    previous = row["tax_position"]
    receivable = sum((r["cash"] for r in taxes.refunds), Decimal(0))
    position = taxes.owed - receivable
    row.update(
        tax_owed=taxes.owed,
        tax_refund_receivable=receivable,
        tax_position=position,
        annual_tax=dict(taxes.result),
        tax_return_provisional=False,
        terminal_wash_assumption="no_replacements_30_days",
    )
    row["net_wealth"] += previous - position
    elapsed = (lots.scenario.end - lots.scenario.start).days / 365.25
    row["real_net_wealth"] = money(
        row["net_wealth"] / Decimal(str((1 + lots.scenario.inflation) ** elapsed))
    )
