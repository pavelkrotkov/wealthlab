"""Monthly cash observes only reported forecasts and already-closed work years."""

from datetime import date
from decimal import Decimal

from wealthlab.household.calendar import months
from wealthlab.retirement.social_work_positions import Positions, arf_entries, work_entries

ZERO = Decimal(0)


def project(case, baseline, assessed, arfs):
    work = {(r["member"], r["payment_month"]): r for r in assessed}
    current_arf = {(r["member"], r["payment_month"]): r["amount"] for r in arfs if not r["arrears"]}
    ordinary = {(r["member"], r["payment_month"]): r for r in baseline["cash_months"]}
    book = Positions(work_entries(assessed) + arf_entries(arfs))
    result = []
    start, end = date(case.claims.start_year, 1, 1), date(case.claims.end_year, 1, 1)
    for month, following in months(start, end):
        book.observe(month, True)
        pending = []
        for person in case.claims.members:
            key = person.id, month
            pending.append(
                cash_row(
                    person.id,
                    month,
                    ordinary[key],
                    work.get(key),
                    current_arf.get(key, ZERO),
                    book,
                    case.work,
                )
            )
        book.observe(following, False)
        result.extend(dict(**row, **book.snapshot(row["member"])) for row in pending)
    return result


def cash_row(member, month, row, work, extra, book, policy):
    held = work["forecast_withheld"] if work is not None else ZERO
    gross = row["issued_before_offsets"] - held + extra
    settlement = book.settle(member, month, gross, policy.overpayment_recovery_fraction)
    return dict(
        member=member,
        payment_month=month,
        baseline_gross=row["issued_before_offsets"],
        forecast_withheld=held,
        current_arf_increase=extra,
        **settlement,
    )
