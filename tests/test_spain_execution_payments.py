"""Spain observes bank cash and independently applied EUR without duplicating payments."""

from decimal import Decimal

from wealthlab.tax.foreign_credit_example import synthetic
from wealthlab.tax.foreign_credit_inputs import CreditAmount
from wealthlab.tax.spain_execution_facts import SpainTaxBinding
from wealthlab.tax.spain_execution_payments import convert

SOURCE = "Synthetic independently dated spot FX and tax recognition"


def test_usd_bank_payment_and_eur_country_recognition_preserve_actual_cash_and_stable_id():
    record = synthetic().tax_cash[0]
    levy = CreditAmount(
        date="2025-12-15", currency="EUR", amount=10000, usd_per_unit="1.10", fx_source=SOURCE
    )
    cash = CreditAmount(
        date="2025-12-15", currency="USD", amount=11000, usd_per_unit=1, fx_source=SOURCE
    )
    record = record.model_copy(update=dict(value=cash, tax_value=levy))
    binding = SpainTaxBinding(
        annual_id="person_a_2025",
        tax_type="irpf",
        foreign_assessment_id="es_income_2025",
        source=SOURCE,
    )
    result = convert(binding, record, Decimal(9000))
    assert (result.id, result.value.currency, result.value.amount) == (record.id, "USD", 11000)
    assert result.value.euros() == 10000
    assert result.recognized_tax_eur == 9000
    assert result.owner_id == record.owner_id


def test_refund_uses_receipt_fx_for_country_cash_and_keeps_original_payment_link():
    record = synthetic().tax_cash[0]
    record = record.model_copy(
        update=dict(
            kind="refund",
            reverses_id="original_tax",
            value=CreditAmount(
                date="2026-05-31", currency="USD", amount=12600, usd_per_unit=1, fx_source=SOURCE
            ),
            tax_value=CreditAmount(
                date="2026-05-31",
                currency="EUR",
                amount=9000,
                usd_per_unit="1.40",
                fx_source=SOURCE,
            ),
        )
    )
    binding = SpainTaxBinding(
        annual_id="person_a_2025",
        tax_type="irpf",
        foreign_assessment_id="es_income_2025",
        source=SOURCE,
    )
    result = convert(binding, record, Decimal(9000))
    assert result.value.euros() == result.recognized_tax_eur == 9000
    assert result.value.amount == 12600
    assert result.reverses_id == "original_tax"
