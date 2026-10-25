"""Fund current-owner salary reductions after actual employee 401k elections.

The same HSA eligibility book supplies annual capacity. Salary reductions
move earned payroll cash, not external employer wealth; reporting treats
them as employer contributions without a personal above-line deduction.
Federal wage adjustment reuses the existing employee-election mapping but
emits no pension-deferral addback, so payroll wages actually decrease.
"""

from decimal import Decimal

from wealthlab.retirement import hsa
from wealthlab.retirement.hsa_household_events import sync_wallet
from wealthlab.retirement.hsa_inputs import HSAContribution
from wealthlab.retirement.workplace_tax import tax_amounts
from wealthlab.retirement.workplace_wages import gross_wages

ZERO = Decimal(0)


def month(ledger, employee, wallet, gross, taxable, start, end):
    if ledger is None or ledger.plan.payroll is None:
        return taxable, {}
    ledger.begin(start.year, wallet)
    book = ledger.book
    ledger.payroll_opening = (start, counters(book), len(book["rows"]))
    book["cash"] = wallet.cash
    if ledger.investments is not None:
        ledger.investments.advance(book, start)
    remaining = (
        dict(employee.remaining_wages)
        if employee
        else gross_wages(gross, ledger.rules, ledger.members)
    )
    excluded, rows = allocate(ledger, remaining, start, end)
    if ledger.investments is not None:
        ledger.investments.sync_cash(book)
    sync_wallet(ledger, wallet)
    return tax_amounts(taxable, ledger.rules, ledger.members, excluded), dict(
        hsa_payroll_contributions=sum(excluded.values(), ZERO),
        hsa_payroll_unfilled=sum((r["requested"] - r["funded"] for r in rows), ZERO),
    )


def allocate(ledger, remaining, start, end):
    book = ledger.book
    excluded = dict.fromkeys(ledger.members, ZERO)
    offset = len(book["rows"])
    for order in ledger.plan.payroll.orders:
        if start <= order.date < end:
            funded = fund(book, order, remaining)
            excluded[order.owner] += funded
    return excluded, book["rows"][offset:]


def fund(book, order, remaining):
    allowed = min(order.amount, max(ZERO, book["limits"][order.owner] - book["used"][order.owner]))
    wage_cap = min(allowed, remaining[order.owner])
    contribution = HSAContribution(
        **order.model_dump(exclude={"owner", "amount"}),
        source="personal_cash",
        amount=wage_cap,
    )
    hsa.contribute(book, contribution, cafeteria=True)
    row = book["rows"][-1]
    remaining[order.owner] -= row["funded"]
    row.update(
        requested=order.amount,
        blocked_by_limit=order.amount - allowed,
        blocked_by_current_wages=allowed - wage_cap,
    )
    return row["funded"]


def counters(book):
    return {key: book[key] for key in ("personal", "employer", "interest")}


def opening(ledger, start):
    pending = ledger.payroll_opening
    ledger.payroll_opening = None
    if pending is None:
        return counters(ledger.book), len(ledger.book["rows"])
    when, before, offset = pending
    if when != start:
        raise ValueError("Payroll HSA opening must match the current receipt month.")
    return before, offset
