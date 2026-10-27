"""Refresh only the foreign book's owned US credit after actual recognized events.

An unexpected funding gain is economic reality, but supplies no foreign basis
or source facts. A mismatch clears this book's credit and blocks the affected
household result instead of retaining a stale favorable claim.
"""

from wealthlab.tax.foreign_credit import evaluate
from wealthlab.tax.foreign_credit_facts import ForeignCredits
from wealthlab.tax.foreign_credit_inputs import CreditCarry
from wealthlab.tax.foreign_tax_positions import assessed
from wealthlab.tax.foreign_tax_sources import denied_source_reasons


def refresh(book, ledger, when):
    from wealthlab.tax.foreign_tax_withholding import observe

    start, end = ledger.funding_context["period"]
    observe(book, ledger, start, end)
    ledger.case = ledger.case.model_copy(update=dict(foreign_credits=ForeignCredits()))
    case = book.credit_case(when.year, when, annual=ledger.case)
    unresolved = (
        carry_reasons(book, when.year)
        + assessment_reasons(book, when)
        + denied_source_reasons(case)
    )
    if unresolved:
        result = dict(candidate=None, unresolved=unresolved, credit_status="blocked")
        book.credit_results[when.year] = result
        return result
    try:
        result = evaluate(case)
    except ValueError as error:
        result = dict(candidate=None, unresolved=[str(error)], credit_status="blocked")
    apply_permitted(ledger, case, result)
    book.credit_results[when.year] = result
    return result


def opening_carries(book, year):
    first = min(book.profiles)
    if year == first:
        return book.profiles[first].opening_carries
    previous = book.credit_results.get(year - 1, {})
    audit = previous.get("carry_audit")
    if audit is None:
        return denied_opening(previous)
    return unused_opening(audit) + generated_excess(audit)


def unused_opening(audit):
    return [
        vintage(r, r["remaining"], "Prior actual credit audit")
        for r in audit["opening"]
        if r["remaining"] and not r["expired"]
    ]


def generated_excess(audit):
    return [
        vintage(r, r["amount"], "Prior actual excess vintage")
        for r in audit["generated_excess"]
        if r["owner_id"] is not None
    ]


def vintage(row, amount, source):
    return CreditCarry(
        id=row["id"],
        owner_id=row["owner_id"],
        origin_year=row["origin_year"],
        basket=row["basket"],
        available_usd=amount,
        source=source,
    )


def carry_reasons(book, year):
    if year == min(book.profiles):
        return []
    previous = book.credit_results.get(year - 1, {})
    audit = previous.get("carry_audit")
    if previous.get("credit_status", "").startswith("denied"):
        return []
    if audit is None or audit["status"] != "conditional_forward_vintages":
        return ["Prior-year foreign credit/carry disposition needs a supported reconciliation."]
    return []


def apply_permitted(ledger, case, result):
    if result["candidate"] is not None:
        facts = result["inputs"]["annual"]["foreign_credits"]
        # The lower audit's input is the zero-credit baseline; its result owns the claim.
        credit = result["candidate"]["federal"]["foreign_tax_credit"]
        facts.update(regular=str(credit), eligibility=case.eligibility, source=case.source)
        ledger.case = ledger.case.model_copy(
            update=dict(foreign_credits=ForeignCredits.model_validate(facts))
        )


def denied_opening(previous):
    if not previous.get("credit_status", "").startswith("denied"):
        return []
    return [CreditCarry.model_validate(r) for r in previous["inputs"]["opening_carries"]]


def assessment_reasons(book, when):
    result = []
    for assessment in book.plan.assessments:
        if (
            assessment.observed <= when
            and assessment.tax_type == "income"
            and permitted_native(book, assessment.id) > assessed(book, assessment, when)
        ):
            result.append(
                "Prelimited credit facts exceed the observed revised foreign "
                "assessment; reconcile tax facts."
            )
    return result


def permitted_native(book, identity):
    return sum(
        r.creditable_native * (-1 if r.kind == "refund" else 1)
        for aid, r in book.payments
        if aid == identity and r.eligibility == "allowed"
    )
