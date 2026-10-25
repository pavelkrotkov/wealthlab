"""Foreign cash, marked claims and due-but-unpaid tax are separate measurements."""

from decimal import Decimal

from wealthlab.tax.foreign_credit_cash import observe
from wealthlab.tax.foreign_tax_positions import remaining
from wealthlab.tax.foreign_tax_recognition import amount as recognized_amount
from wealthlab.tax.foreign_tax_sources import history

ZERO = Decimal(0)


def report(book, when, positions, unresolved):
    case = book.credit_case(when.year, when).model_copy(update=dict(income=book.income_history()))
    all_rows = observe(case)
    ids = {r.id for r in book.month_records}
    cash = enrich(book, [r for r in all_rows if r["id"] in ids])
    outflow = sum((r["observed_cash_outflow_usd"] for r in cash), ZERO)
    position = sum((r["marked_position_usd"] for r in positions), ZERO)
    return dict(
        foreign_tax_cash_outflow=outflow,
        foreign_tax_paid=sum((max(ZERO, r["observed_cash_outflow_usd"]) for r in cash), ZERO),
        foreign_tax_refund_received=sum(
            (max(ZERO, -r["observed_cash_outflow_usd"]) for r in cash), ZERO
        ),
        foreign_tax_position=position,
        foreign_tax_positions=positions,
        foreign_tax_cash_records=cash,
        foreign_tax_credit=book.credit_results[when.year],
        foreign_tax_source_identities=history(book.profiles.values(), when)[1],
        foreign_tax_unfunded=due_shortfall(book, when),
        foreign_tax_unresolved=sorted(set(unresolved)),
    )


def due_shortfall(book, when):
    from wealthlab.household.calendar import money

    due = {}
    for schedule in book.plan.schedules:
        if schedule.due_date <= when:
            due[schedule.assessment_id] = due.get(schedule.assessment_id, ZERO) + (
                schedule.requested_native - book.filled[schedule.id]
            )
    total = ZERO
    for identity, requested in due.items():
        assessment = book.assessments[identity]
        if assessment.observed <= when:
            native = min(requested, max(ZERO, remaining(book, assessment, when)))
            total += native * book.quotes[(when, assessment.currency)].usd_per_unit
    return money(total)


def enrich(book, rows):
    assessments = {record.id: book.assessments[identity] for identity, record in book.payments}
    records = {record.id: record for _, record in book.payments}
    return [
        dict(
            row,
            assessment_id=assessments[row["id"]].id,
            payment_schedule_id=book.schedule_by_payment.get(row["id"]),
            tax_type=assessments[row["id"]].tax_type,
            fx_fee_usd=records[row["id"]].fx_fee_usd,
            gross_cash_usd=records[row["id"]].value.dollars(),
            local_recognized_tax_native=recognized_amount(book, records[row["id"]]),
        )
        for row in rows
    ]
