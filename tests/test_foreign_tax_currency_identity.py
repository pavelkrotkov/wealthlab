"""Actual USD bank cash and EUR levy translation retain different identities and quotes.

A EUR10,000 levy paid with USD11,000 uses paid-date1.1. A EUR1,000
refund received as USD1,400 reverses USD1,100 credit at original1.1,
while its USD300 currency difference needs separately recognized income.
"""

from decimal import Decimal

import pytest

from wealthlab.tax.foreign_credit import evaluate
from wealthlab.tax.foreign_credit_cash import observe
from wealthlab.tax.foreign_credit_example import amount, synthetic
from wealthlab.tax.foreign_credit_inputs import ForeignCreditCase


def currencies():
    data = synthetic().model_dump(mode="json")
    original = data["tax_cash"][0]
    original["value"] = amount("2025-06-30", 11000)
    original["tax_value"] = amount("2025-06-30", 10000, "EUR", "1.1")
    refund = dict(
        original,
        id="refund",
        kind="refund",
        reverses_id=original["id"],
        value=amount("2025-12-15", 1400),
        tax_value=amount("2025-12-15", 1000, "EUR", "1.4"),
        creditable_native="1000",
        fx_income_id="fx_income",
    )
    data["tax_cash"].append(refund)
    data["income"].append(
        dict(
            id="fx_income",
            owner_id="person_a",
            country="US",
            kind="ordinary",
            basket="general",
            value=amount("2025-12-15", 300),
            source_classification="Supplied positive ordinary FX income classification",
        )
    )
    data["annual"]["federal_income"]["ordinary_noninvestment_income"] = "300"
    data["fx_income_treatment"] = "included_in_annual_facts"
    return data


def test_cash_currency_and_original_levy_fx_preserve_actual_refund_cash():
    result = evaluate(ForeignCreditCase.model_validate(currencies()))
    original, refund = result["actual_tax_cash"]
    assert original["observed_cash_outflow_usd"] == original["credit_tax_usd"] == 11000
    assert refund["observed_cash_outflow_usd"] == -1400
    assert refund["credit_tax_usd"] == -1100
    assert refund["refund_fx_difference_usd"] == 300
    assert (refund["currency"], refund["tax_currency"]) == ("USD", "EUR")
    assert result["observed_tax_cash_outflow_usd"] == 9600


@pytest.mark.parametrize(
    "change, message",
    [
        (lambda d: d["tax_cash"][0]["tax_value"].update(date="2025-06-29"), "translation date"),
        (lambda d: d["tax_cash"][0]["tax_value"].update(usd_per_unit="1.2"), "must reconcile"),
        (lambda d: d["tax_cash"][1]["tax_value"].update(currency="GBP"), "timing/currency"),
    ],
)
def test_unreconciled_paid_dates_cash_translation_or_original_levy_currency_reject(change, message):
    data = currencies()
    change(data)
    with pytest.raises(ValueError, match=message):
        observe(ForeignCreditCase.model_validate(data))


def test_foreign_native_refund_cap_is_not_a_cap_on_appreciated_usd_cash():
    data = currencies()
    original = data["tax_cash"][0]
    original.update(
        value=amount("2025-06-30", 1100),
        tax_value=amount("2025-06-30", 1000, "EUR", "1.1"),
        creditable_native="1000",
    )
    rows = observe(ForeignCreditCase.model_validate(data))
    assert rows[1]["observed_cash_outflow_usd"] == -1400
    assert rows[1]["credit_tax_usd"] == -1100
    assert rows[1]["refund_fx_difference_usd"] == Decimal(300)
