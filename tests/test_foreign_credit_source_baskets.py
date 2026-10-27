"""A tax payment cannot claim another basket's larger limit or create misplaced carry."""

from decimal import Decimal

import pytest
from foreign_basket_cases import mixed_income, split_payment

from wealthlab.tax.foreign_credit import evaluate
from wealthlab.tax.foreign_credit_inputs import ForeignCreditCase


def test_passive_tax_linked_only_to_general_wages_rejects_the_4155_10_false_credit():
    data = mixed_income()
    data["tax_cash"][0]["basket"] = "passive"
    with pytest.raises(ValueError, match="linked source basket"):
        evaluate(ForeignCreditCase.model_validate(data))


def test_correct_wage_basket_preserves_5500_cash_and_general_excess_vintage():
    result = evaluate(ForeignCreditCase.model_validate(mixed_income()))
    excess = result["carry_audit"]["generated_excess"]
    assert result["candidate"]["federal"]["foreign_tax_credit"] == Decimal("1344.90")
    assert result["observed_tax_cash_outflow_usd"] == 5500
    assert excess[0]["amount"] == Decimal("4155.10")
    assert (excess[0]["basket"], excess[0]["origin_year"]) == ("general", 2025)


def test_explicit_split_records_keep_one_cash_total_and_only_the_wages_excess():
    result = evaluate(split_payment())
    assert result["observed_tax_cash_outflow_usd"] == 5500
    assert result["candidate"]["federal"]["foreign_tax_credit"] == Decimal("4844.90")
    assert result["candidate"]["federal"]["income_tax"] == Decimal("8604.10")
    assert result["carry_audit"]["generated_excess"][0]["amount"] == Decimal("655.10")
    assert result["carry_audit"]["generated_excess"][0]["basket"] == "general"
