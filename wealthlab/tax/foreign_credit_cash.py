"""Observe actual foreign tax cash and independently translated credit amounts.

Positive outflow denotes a payment/withholding plus explicit FX fees; a refund
has the opposite cash sign and retains its receipt-date quote. Credit reversal
uses the original payment quote. This standalone audit deposits no cash and
reports no forecast refund: linked household execution belongs to its consumer.
"""

from decimal import Decimal

from wealthlab.household.calendar import money
from wealthlab.tax.foreign_credit_refunds import validate_refund
from wealthlab.tax.foreign_tax_translation import tax_value
from wealthlab.tax.foreign_tax_translation import validate as validate_translation

ZERO = Decimal(0)


def observe(case):
    records = {r.id: r for r in case.tax_cash}
    income = {r.id: r for r in case.income}
    rows = []
    for record in case.tax_cash:
        validate_record(record, records, income)
        original = records[record.reverses_id] if record.kind == "refund" else record
        rows.append(
            dict(
                id=record.id,
                owner_id=record.owner_id,
                country=record.country,
                date=record.value.date.isoformat(),
                liability_year=record.liability_year,
                basket=record.basket,
                kind=record.kind,
                currency=record.value.currency,
                native_amount=record.value.amount,
                cash_fx=record.value.usd_per_unit,
                cash_fx_source=record.value.fx_source,
                tax_currency=tax_value(record).currency,
                tax_native_amount=tax_value(record).amount,
                tax_paid_date=tax_value(record).date.isoformat(),
                tax_spot_fx=tax_value(record).usd_per_unit,
                tax_fx_source=tax_value(record).fx_source,
                **translated(record, original),
                credit_year=original.value.date.year,
                original_payment_id=original.id,
            )
        )
    return rows


def validate_record(record, records, income):
    validate_translation(record)
    if record.creditable_native > tax_value(record).amount:
        raise ValueError("Creditable tax cannot exceed the actually observed native tax amount.")
    if any(identity not in income for identity in record.income_ids):
        raise ValueError("Tax cash must link known included-income source identities.")
    validate_income_owner(record, income)
    if record.kind == "refund":
        validate_refund(record, records)
    elif record.reverses_id is not None:
        raise ValueError("Only a tax refund reverses an original tax payment.")


def validate_income_owner(record, income):
    if record.tax_type == "income" and record.creditable_native and not record.income_ids:
        raise ValueError("Creditable income tax needs a linked recognized-income source.")
    if any(income[identity].owner_id != record.owner_id for identity in record.income_ids):
        raise ValueError("A tax payment cannot silently claim another person's source income.")


def translated(record, original):
    sign = -1 if record.kind == "refund" else 1
    qualified = record.eligibility == "allowed" and record.tax_type == "income"
    credit = money(record.creditable_native * tax_value(original).usd_per_unit)
    original_value = money(tax_value(record).amount * tax_value(original).usd_per_unit)
    return dict(
        observed_cash_outflow_usd=sign * record.value.dollars() + record.fx_fee_usd,
        refund_fx_difference_usd=(
            record.value.dollars() - original_value if record.kind == "refund" else ZERO
        ),
        credit_fx=tax_value(original).usd_per_unit,
        credit_tax_usd=sign * credit if qualified else ZERO,
    )
