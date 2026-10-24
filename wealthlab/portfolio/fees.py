"""Assess same-date fees against one snapshot; unpaid cash charges remain liabilities.

Embedded fee estimates are disclosure only: supplied prices already include them.
Cash fees have no automatic tax deduction. Contract bases and day counts are inputs.
"""

from decimal import Decimal

from wealthlab.household.calendar import money


def basis(book, schedule, period):
    if period.supplied_base is not None:
        return period.supplied_base
    securities = set(schedule.security_ids) or set(book.securities)
    value = sum(
        lot.quantity * period.prices[lot.security_id]
        for lot in book.lots.values()
        if lot.account_id in schedule.account_ids and lot.security_id in securities
    )
    cash = sum(book.cash[key] for key in schedule.account_ids) if schedule.include_cash else 0
    return money(value + cash)


def assessment(book, schedule, period):
    base = basis(book, schedule, period)
    days = (period.date - period.start).days
    charge = money(base * schedule.annual_rate * days / schedule.day_count)
    return dict(
        schedule=schedule.id,
        kind=schedule.kind,
        date=period.date.isoformat(),
        payment_account=schedule.payment_account,
        treatment=schedule.treatment,
        valuation_base=base,
        base_source="supplied" if period.supplied_base is not None else "current holdings",
        period_days=days,
        assessed=charge + schedule.fixed_per_period,
    )


def assess_date(case, book, when):
    rows = [
        assessment(book, schedule, period)
        for schedule in case.fee_schedules
        for period in schedule.periods
        if period.date == when
    ]
    # Compute all bases before any payment so schedule order cannot change cash-inclusive fees.
    for row in rows:
        if row["treatment"] == "cash":
            book.fee_owed[row["payment_account"]] += row["assessed"]
    book.fee_assessments.extend(rows)
    for account in book.accounts:
        settle(book, account)


def settle(book, account):
    payment = min(book.fee_owed[account], book.cash[account])
    book.cash[account] -= payment
    book.fee_owed[account] -= payment
    book.fee_paid[account] += payment


def summary(book):
    def total(treatment):
        return sum(
            (row["assessed"] for row in book.fee_assessments if row["treatment"] == treatment),
            Decimal(0),
        )

    return dict(
        cash_assessed=total("cash"),
        cash_paid=sum(book.fee_paid.values(), Decimal(0)),
        cash_owed=sum(book.fee_owed.values(), Decimal(0)),
        embedded_estimate=total("embedded_in_prices"),
    )
