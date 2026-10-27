"""A foreign assessment less actual net paid tax creates one payable or receivable.

A delayed refund is an asset only after the assessment establishes it. It
cannot fund a payment until the actual receipt. Current dated quotes value
remaining native positions without changing their tax-credit translation.
"""

from decimal import Decimal

from wealthlab.household.calendar import money
from wealthlab.tax.foreign_tax_recognition import amount as recognized_amount

ZERO = Decimal(0)


def assessed(book, assessment, when):
    if assessment.observed > when:
        return ZERO
    value = assessment.amount_native
    revisions = sorted(book.plan.revisions, key=lambda row: row.observed)
    for revision in revisions:
        if revision.assessment_id == assessment.id and revision.observed <= when:
            value = revision.amount_native
    return value


def net_paid(book, assessment_id):
    return sum(
        (
            recognized_amount(book, r) * (-1 if r.kind == "refund" else 1)
            for identity, r in book.payments
            if identity == assessment_id
        ),
        ZERO,
    )


def remaining(book, assessment, when):
    return assessed(book, assessment, when) - net_paid(book, assessment.id)


def snapshot(book, when):
    rows = []
    for assessment in book.plan.assessments:
        if assessment.observed > when:
            continue
        native = remaining(book, assessment, when)
        quote = book.quotes[(when, assessment.currency)]
        rows.append(
            dict(
                assessment_id=assessment.id,
                owner_id=assessment.owner_id,
                country=assessment.country,
                liability_year=assessment.liability_year,
                tax_type=assessment.tax_type,
                assessment_status=assessment.eligibility,
                currency=assessment.currency,
                assessed_native=assessed(book, assessment, when),
                actual_net_paid_native=net_paid(book, assessment.id),
                remaining_native=native,
                marked_position_usd=recognized_position(assessment, native, quote),
                refund_claim_status=assessment.refund_claim_eligibility,
                contingent_refund_marked_usd=contingent_refund(assessment, native, quote),
                quote_date=when.isoformat(),
                usd_per_unit=quote.usd_per_unit,
                assessed_marked_usd=money(assessed(book, assessment, when) * quote.usd_per_unit),
                fx_source=quote.source,
                source=assessment.source,
            )
        )
    return rows


def recognized_position(assessment, native, quote):
    if native < 0 and assessment.refund_claim_eligibility != "allowed":
        return ZERO
    return money(native * quote.usd_per_unit)


def contingent_refund(assessment, native, quote):
    if native < 0 and assessment.refund_claim_eligibility != "allowed":
        return money(-native * quote.usd_per_unit)
    return ZERO


def position_reasons(book, positions):
    result = []
    for position in positions:
        if position["contingent_refund_marked_usd"]:
            result.append(
                "Foreign refund-claim eligibility is unresolved/denied; "
                "contingent value is excluded."
            )
        identity = position["assessment_id"]
        covered = sum(
            (
                s.requested_native - book.filled[s.id]
                for s in book.plan.schedules
                if s.assessment_id == identity
            ),
            ZERO,
        )
        if position["remaining_native"] > covered:
            result.append("A remaining foreign assessment lacks a complete payment schedule.")
    return result
