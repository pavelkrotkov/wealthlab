"""Independent section72 basis identities; loan cash is not itself economic gain."""

from tests.life_contract_cases import case, event
from wealthlab.products.life_contract import run


def test_non_mec_withdrawal_recovers_basis_then_surrender_recognizes_remaining_gain():
    result = run(case([event("withdrawal", 40), event("surrender", 125, 2)]))
    assert result["rows"][0]["federal_ordinary_income"] == 0
    assert result["rows"][0]["federal_basis_after"] == 60
    assert result["rows"][1]["federal_ordinary_income"] == 65
    assert result["external_cash"] == 165
    assert result["closed_contract_asset"] == 0
    assert result["closing_federal_basis"] == 0


def test_revenue_ruling_2009_13_surrender_example_uses_full_premium_basis():
    result = run(case([event("surrender", 78000)], opening_federal_basis="64000"))
    assert result["rows"][0]["federal_ordinary_income"] == 14000
    assert result["rows"][0]["federal_additional_tax"] == 0


def test_mec_taxed_loan_increases_basis_and_repayment_is_not_a_second_premium():
    events = [
        event("loan_advance", 40, cash_value_before="150"),
        event("loan_principal_repayment", 20, 2),
        event("withdrawal", 20, 3, cash_value_before="150"),
        event("surrender", 130, 4),
    ]
    result = run(case(events, federal_status="mec"))
    rows = result["rows"]
    assert [r["federal_ordinary_income"] for r in rows] == [40, 0, 10, 0]
    assert [r["federal_basis_after"] for r in rows] == [140, 140, 130, 0]
    assert [r["federal_additional_tax"] for r in rows] == [4, 0, 1, 0]
    assert [r["loan_after"] for r in rows] == [40, 20, 20, 0]
    assert result["external_cash"] == 150


def test_mec_capitalized_interest_is_a_new_loan_without_external_cash():
    result = run(
        case(
            [
                event("loan_advance", 40, cash_value_before="150"),
                event("capitalized_interest", 10, 2, cash_value_before="150"),
                event("surrender", 150, 3),
            ],
            federal_status="mec",
        )
    )
    assert [r["federal_ordinary_income"] for r in result["rows"]] == [40, 10, 0]
    assert [r["external_cash"] for r in result["rows"]] == [40, 0, 100]
    assert result["external_cash"] == 140


def test_mec_pre_charge_cash_value_and_non_taxable_receipts_are_distinct():
    result = run(
        case(
            [
                event("withdrawal", 60, cash_value_before="150"),
                event("surrender", 85, 2),
            ],
            federal_status="mec",
        )
    )
    assert result["rows"][0]["federal_ordinary_income"] == 50
    assert result["rows"][0]["federal_basis_after"] == 90
    assert result["rows"][1]["federal_ordinary_income"] == 0
    assert result["closing_federal_basis"] == 0  # personal surrender loss is not deducted
