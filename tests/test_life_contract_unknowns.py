"""Unconfirmed tax classification cannot silently become a tax-free strategy."""

import pytest

from tests.life_contract_cases import case, event
from wealthlab.products.life_contract import run


@pytest.mark.parametrize(
    "updates",
    [
        {"federal_status": "unknown"},
        {"opening_federal_basis": None},
        {"ordinary_personal_contract_confirmed": False},
        {"no_aggregation_or_special_basis_adjustments_confirmed": False},
        {"withdrawals_without_early_benefit_recapture_confirmed": False},
    ],
)
def test_unknown_basis_or_eligibility_withholds_tax_and_carries_unknown_basis(updates):
    result = run(case([event("withdrawal", 40), event("surrender", 125, 2)], **updates))
    assert all(r["federal_ordinary_income"] is None for r in result["rows"])
    assert result["annual"][0]["tax_change"] is None
    assert "federal_ordinary_income" in result["annual"][0]["unknown_fields"]
    assert result["external_cash"] == 165


def test_mec_missing_pre_event_value_or_capitalization_terms_is_unknown():
    result = run(case([event("loan_advance", 10)], federal_status="mec"))
    assert result["rows"][0]["federal_ordinary_income"] is None
    result = run(
        case(
            [event("capitalized_interest", 2, cash_value_before="150")],
            federal_status="mec",
            opening_loan="20",
            capitalized_interest_is_new_loan_confirmed=False,
        )
    )
    assert result["rows"][0]["federal_basis_after"] is None
    assert result["closing_loan"] == 22


def test_nj_recognition_is_independent_and_missing_is_not_zero():
    flow = event("surrender", 150)
    flow["nj_ordinary_income"] = None
    result = run(case([flow]))
    assert result["rows"][0]["federal_ordinary_income"] == 50
    assert result["annual"][0]["unknown_fields"] == ["nj_ordinary_income"]
    assert result["annual"][0]["tax_change"] is None
