"""Unknown tax facts preserve observed money while unsafe source identities reject.

These cases exercise the trust boundary rather than assuming that a foreign
bill establishes US creditability. A required original-year revision, an
induced AMT liability and a stale source denominator each prevent the annual
bridge from publishing a favorable credit result.
"""

from decimal import Decimal

import pytest

from wealthlab.tax.foreign_credit import evaluate
from wealthlab.tax.foreign_credit_example import synthetic
from wealthlab.tax.foreign_credit_inputs import ForeignCreditCase


@pytest.mark.parametrize("change", ["basket", "eligibility", "included", "us_tax", "amt"])
def test_unresolved_or_unsupported_tax_profiles_do_not_hide_actual_cash(change):
    data = synthetic().model_dump(mode="json")
    tax = data["tax_cash"][0]
    if change == "basket":
        tax["basket"] = "treaty_resourced"
    elif change == "eligibility":
        tax["eligibility"] = "unresolved"
    elif change == "included":
        tax["included_income_confirmed"] = False
    elif change == "us_tax":
        tax["country"] = "US"
    else:
        data["income"][0]["country"] = "ES"
    result = evaluate(ForeignCreditCase.model_validate(data))
    assert result["candidate"] is None
    assert result["unresolved"]
    assert result["observed_tax_cash_outflow_usd"] == Decimal(11000)


@pytest.mark.parametrize("change", ["date", "role", "duplicate", "usd", "future", "opening"])
def test_invalid_observation_or_ownership_cannot_create_a_credit(change):
    data = synthetic().model_dump(mode="json")
    if change == "date":
        data["as_of"] = "2026-12-31"
    elif change == "role":
        data["people"]["person_a"] = "spouse"
    elif change == "duplicate":
        data["tax_cash"][0]["id"] = data["income"][0]["id"]
    elif change == "usd":
        data["income"][0]["value"]["usd_per_unit"] = "2"
    elif change == "future":
        data["as_of"] = "2025-07-01"
    else:
        data["opening_carries"] = [
            dict(
                id="new",
                owner_id="person_a",
                origin_year=2025,
                basket="general",
                available_usd="100",
                source="Synthetic invalid opening vintage",
            )
        ]
    with pytest.raises(ValueError):
        evaluate(ForeignCreditCase.model_validate(data))


def test_nonincome_wealth_tax_and_conversion_fee_reduce_cash_without_an_income_credit():
    data = synthetic().model_dump(mode="json")
    data["tax_cash"][0].update(tax_type="wealth", income_ids=[], fx_fee_usd="15")
    result = evaluate(ForeignCreditCase.model_validate(data))
    assert result["observed_tax_cash_outflow_usd"] == Decimal(11015)
    assert result["candidate"]["federal"]["foreign_tax_credit"] == 0
    assert result["candidate"]["federal"]["income_tax"] == Decimal(13449)


def test_source_total_mismatch_cannot_reduce_the_worldwide_denominator():
    data = synthetic().model_dump(mode="json")
    data["income"][0]["value"]["amount"] = "40000"
    with pytest.raises(ValueError, match="exactly reconcile"):
        evaluate(ForeignCreditCase.model_validate(data))
