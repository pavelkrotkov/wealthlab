"""Contradictory known categories reject before payment, withholding or refund credit use."""

import pytest
from foreign_basket_cases import mixed_income

from wealthlab.tax.foreign_credit_cash import observe
from wealthlab.tax.foreign_credit_inputs import ForeignCreditCase


@pytest.mark.parametrize("basket", ["general", "passive"])
def test_one_positive_credit_record_cannot_span_two_known_income_baskets(basket):
    data = mixed_income()
    data["tax_cash"][0].update(basket=basket, income_ids=["work_us", "work_es"])
    with pytest.raises(ValueError, match="split mixed payments"):
        observe(ForeignCreditCase.model_validate(data))
