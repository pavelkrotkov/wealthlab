"""Monthly premium accrual and FIFO cash payments, with dated arrears."""

from collections import deque
from decimal import Decimal

from wealthlab.household.calendar import months
from wealthlab.retirement.contribution_inputs import CashReceipt
from wealthlab.retirement.medicare_history import income_for
from wealthlab.retirement.medicare_rules import SOURCE, premiums, scale


def run(case):
    """Enrollment continues as supplied even if funding fails; this is a cash stress case.

    Premiums are due on the first of their coverage month, an explicit planning
    convention rather than an assertion about Medicare's actual billing dates.
    Later cash pays the oldest unpaid bill first and records its real payment date.
    """
    book = dict(cash=case.opening_cash, rows=[], payments=[], pending=deque())
    events = [(r.date, 0, index, r) for index, r in enumerate(case.receipts)]
    events += bills(case)
    for when, _, _, event in sorted(events, key=lambda item: item[:3]):
        if isinstance(event, CashReceipt):
            book["cash"] += event.amount
        else:
            book["rows"].append(event)
            book["pending"].append(event)
        pay(book, when)
        if not isinstance(event, CashReceipt):
            event["unfunded_at_due"] = event["unfunded"]
    return dict(
        cash=book["cash"],
        monthly=book["rows"],
        payments=book["payments"],
        total_due=sum((r["total_due"] for r in book["rows"]), Decimal(0)),
        total_paid=sum((p["amount"] for p in book["payments"]), Decimal(0)),
        outstanding=sum((r["unfunded"] for r in book["rows"]), Decimal(0)),
        rule_base_year=2026,
        future_policy=case.future_policy,
        premium_growth=case.premium_growth,
        threshold_growth=case.threshold_growth,
        sources=[SOURCE, "https://secure.ssa.gov/POMS.NSF/LNX/0601101010"],
    )


def bills(case):
    events = []
    for index, coverage in enumerate(case.coverage):
        for start, _ in months(coverage.start, coverage.end):
            events.append((start, 1, index, quote(case, coverage, start)))
    return events


def quote(case, coverage, when):
    income, method, rates = income_quote(case, coverage, when.year)
    part_a = scale(case, when.year, coverage.part_a_monthly_2026, "premium")
    part_b = rates["b_total"] if coverage.part_b else Decimal(0)
    part_d = Decimal(0)
    if coverage.part_d:
        part_d = scale(case, when.year, coverage.part_d_plan_monthly_2026, "premium")
        part_d += rates["d_irmaa"]
    other = scale(case, when.year, coverage.other_monthly_health_cost_2026, "premium")
    total = part_a + part_b + part_d + other
    return dict(
        id=f"{coverage.id}:{when:%Y%m}",
        date=when,
        member=coverage.member,
        income_record=None if income is None else income.id,
        income_year=None if income is None else income.year,
        determination=method,
        magi=rates["magi"],
        tier=rates["tier"],
        part_a=part_a,
        part_b=part_b,
        b_irmaa=rates["b_irmaa"] if coverage.part_b else Decimal(0),
        part_d=part_d,
        d_irmaa=rates["d_irmaa"] if coverage.part_d else Decimal(0),
        other_health=other,
        total_due=total,
        paid=Decimal(0),
        unfunded=total,
        rule_mode="published_2026" if when.year == 2026 else case.future_policy,
    )


def income_quote(case, coverage, year):
    if coverage.part_b or coverage.part_d:
        income, method = income_for(case, coverage.member, year)
        return income, method, premiums(case, year, income)
    return None, "no_income_related_coverage", dict(magi=None, tier=None, b_irmaa=0, d_irmaa=0)


def pay(book, when):
    while book["pending"] and book["cash"] > 0:
        row = book["pending"][0]
        amount = min(book["cash"], row["unfunded"])
        book["cash"] -= amount
        row["paid"] += amount
        row["unfunded"] -= amount
        if amount:
            book["payments"].append(
                dict(date=when, due=row["id"], member=row["member"], amount=amount)
            )
        if not row["unfunded"]:
            book["pending"].popleft()
