"""Contradictory known categories reject before payment, withholding or refund credit use."""

import pytest
from foreign_basket_cases import mixed_income

from wealthlab.tax.foreign_credit_cash import observe
from wealthlab.tax.foreign_credit_example import amount
from wealthlab.tax.foreign_credit_inputs import ForeignCreditCase


@pytest.mark.parametrize("basket", ["general", "passive"])
def test_one_positive_credit_record_cannot_span_two_known_income_baskets(basket):
    data = mixed_income()
    data["tax_cash"][0].update(basket=basket, income_ids=["work_us", "work_es"])
    with pytest.raises(ValueError, match="split mixed payments"):
        observe(ForeignCreditCase.model_validate(data))


@pytest.mark.parametrize("eligibility", ["allowed", "denied", "unresolved"])
@pytest.mark.parametrize("kind", ["payment", "withholding", "refund"])
def test_record_kind_or_eligibility_cannot_erase_a_positive_source_basket_contradiction(
    eligibility, kind
):
    data = mixed_income()
    tax = data["tax_cash"][0]
    changed = dict(
        tax,
        id="changed",
        kind=kind,
        eligibility=eligibility,
        basket="general",
        income_ids=["work_es"],
    )
    if kind == "refund":
        changed.update(
            reverses_id=tax["id"], value=amount("2025-12-20", 1000), creditable_native="1000"
        )
    data["tax_cash"].append(changed)
    with pytest.raises(ValueError, match="linked source basket"):
        observe(ForeignCreditCase.model_validate(data))
