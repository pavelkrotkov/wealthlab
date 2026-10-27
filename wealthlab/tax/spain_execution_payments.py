"""Translate observed cash for Spain without a second wallet movement or an annual FX rate.

Country recognition stays independent of US creditable tax. The actual bank
currency/date and levy-date EUR quote determine each payment conversion;
refunds preserve their original globally unique payment identity.
"""

from wealthlab.tax.foreign_tax_sources import payment_record
from wealthlab.tax.foreign_tax_translation import tax_value
from wealthlab.tax.spain_payment_records import SpanishTaxPayment


def observed_payments(scenario, observed):
    if observed is not None:
        return observed["foreign_payments"], observed["foreign_recognized_native"]
    plan = scenario.foreign_tax_plan
    payments = [(p.assessment_id, payment_record(p)) for p in plan.opening_payments]
    amounts = {
        p.record.id: p.recognized_tax_native
        for p in plan.opening_payments
        if p.recognized_tax_native is not None
    }
    return payments, amounts


def convert(binding, record, recognized_native):
    levy = tax_value(record)
    if levy.currency != "EUR":
        raise ValueError("Spain cash needs its separately dated EUR levy conversion.")
    rate = record.value.usd_per_unit / levy.usd_per_unit
    return SpanishTaxPayment(
        id=record.id,
        owner_id=record.owner_id,
        liability_year=record.liability_year,
        tax_type=binding.tax_type,
        kind=record.kind,
        value=dict(
            date=record.value.date,
            amount=record.value.amount,
            currency=record.value.currency,
            eur_per_unit=rate,
            source=record.value.fx_source + "; EUR levy quote: " + levy.fx_source,
        ),
        recognized_tax_eur=recognized_native,
        tax_recognition_source=record.source,
        reverses_id=record.reverses_id,
    )


def payments(scenario, execution, observed):
    records, applied = observed_payments(scenario, observed)
    bindings = {b.foreign_assessment_id: b for b in execution.bindings}
    result = {a.id: [] for a in execution.assessments.annuals}
    for identity, record in records:
        if identity not in bindings:
            continue
        binding = bindings[identity]
        amount = applied.get(record.id, tax_value(record).amount)
        result[binding.annual_id].append(convert(binding, record, amount))
    return result
