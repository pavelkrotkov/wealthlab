"""Settle actual affordable native tax with the existing wallet and sale solver.

A monthly payment is capped by both its remaining schedule and the assessment
less actual net paid tax. Native cents round down before USD settlement; the
cent-rounded debit and explicit per-execution fee must fit available cash.
Only actual paid native tax enters the credit history. The shared funding
solver retains domestic tax and spending requirements and creates no loan.
"""

from decimal import ROUND_DOWN, Decimal
from hashlib import sha256

from wealthlab.household.calendar import money
from wealthlab.tax.foreign_credit_inputs import CreditAmount, CreditTaxCash
from wealthlab.tax.foreign_tax_positions import remaining
from wealthlab.tax.foreign_tax_sources import schedule_sources

ZERO = Decimal(0)
CENT = Decimal(".01")


def pay_due(book, ledger, wallet, start, end, when):
    for schedule in sorted(book.plan.schedules, key=lambda s: (s.due_date, s.id)):
        assessment = book.assessments[schedule.assessment_id]
        if schedule.due_date > when or assessment.observed > when:
            continue
        wanted = min(
            schedule.requested_native - book.filled[schedule.id],
            max(ZERO, remaining(book, assessment, when)),
        )
        if not wanted or assessment.eligibility != "allowed":
            continue
        quote = book.quotes[(when, assessment.currency)]
        requested = money(wanted * quote.usd_per_unit) + schedule.fee_per_execution_usd
        if book.plan.allow_household_sales:
            ledger.fund_required(wallet, requested, start, end)
        amount = affordable(wallet.cash, wanted, quote.usd_per_unit, schedule.fee_per_execution_usd)
        if amount:
            sequence = book.executions.get((schedule.id, quote.date), 0) + 1
            record = payment(schedule, assessment, amount, quote, sequence)
            commit(book, wallet, assessment, schedule, record, amount)


def commit(book, wallet, assessment, schedule, record, amount):
    if record.id in book.observed_ids() or record.id in book.reserved_ids:
        raise ValueError("Generated foreign payment identity is already observed or reserved.")
    cost = record.value.dollars() + record.fx_fee_usd
    if wallet.pay(cost) != cost:
        raise ValueError("Foreign native tax settlement and available wallet cash disagree.")
    book.payments.append((assessment.id, record))
    book.filled[schedule.id] += amount
    key = (schedule.id, record.value.date)
    book.executions[key] = book.executions.get(key, 0) + 1
    book.schedule_by_payment[record.id] = schedule.id
    book.month_records.append(record)


def affordable(cash, requested, rate, fee):
    budget = max(ZERO, cash - fee)
    return min(requested, (budget / rate).quantize(CENT, rounding=ROUND_DOWN))


def payment(schedule, assessment, amount, quote, sequence=1):
    return CreditTaxCash(
        id=payment_id(schedule.id, quote.date, sequence),
        owner_id=assessment.owner_id,
        country=assessment.country,
        liability_year=assessment.liability_year,
        tax_type=assessment.tax_type,
        kind="payment",
        basket=schedule.basket,
        value=CreditAmount(
            date=quote.date,
            currency=quote.currency,
            amount=amount,
            usd_per_unit=quote.usd_per_unit,
            fx_source=quote.source,
        ),
        fx_fee_usd=schedule.fee_per_execution_usd,
        creditable_native=money(amount * schedule.creditable_fraction),
        eligibility=schedule.credit_eligibility,
        included_income_confirmed=schedule.included_income_confirmed,
        income_ids=schedule_sources(schedule, assessment.owner_id),
        source=schedule.source,
    )


def payment_id(schedule, when, sequence):
    first = f"{schedule}_{when.isoformat().replace('-', '_')}"
    if sequence == 1:
        return first
    # Preserve the first-payment identity used by supplied refund links. Later
    # real executions have bounded stable IDs and retain their schedule audit.
    return "foreign_pay_" + sha256(f"{first}:{sequence}".encode()).hexdigest()[:40]
