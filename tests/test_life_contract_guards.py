"""Only supported executed paths can produce policy and tax results."""

import pytest

from tests.life_contract_cases import case, event
from wealthlab.products.life_contract import run


@pytest.mark.parametrize(
    "events,updates,message",
    [
        ([event("loan_principal_repayment", 1)], {}, "exceeds"),
        ([event("surrender", 90)], {"opening_loan": "100"}, "discharge-tax"),
        ([event("lapse", 100), event("premium", 1, 2)], {}, "follow"),
        ([event("premium", 1, 2)], {"stop_funding_date": "2025-06-01"}, "stop-funding"),
        ([event("premium", 1, 2), event("premium", 1)], {}, "execution order"),
        ([event("premium", 1), event("premium", 1)], {}, "unique"),
        ([event("premium", 1)], {"start": "2026-01-01"}, "opening snapshot"),
        ([], {"issue_date": "1960-01-01"}, "ordered"),
    ],
)
def test_inconsistent_contracts_are_rejected(events, updates, message):
    with pytest.raises(ValueError, match=message):
        run(case(events, **updates))


def test_half_birthday_and_explicit_exceptions_control_mec_additional_tax():
    before = case([event("withdrawal", 20, cash_value_before="150")], federal_status="mec")
    assert run(before)["rows"][0]["federal_additional_tax"] == 2
    older = case(
        [event("withdrawal", 20, cash_value_before="150")],
        federal_status="mec",
        owner_birth_date="1965-12-01",
    )
    assert run(older)["rows"][0]["federal_additional_tax"] == 0
    exempt = case(
        [event("withdrawal", 20, cash_value_before="150")],
        federal_status="mec",
        additional_tax_exception="disability_confirmed",
    )
    assert run(exempt)["rows"][0]["federal_additional_tax"] == 0


def test_unconfirmed_life_contract_cannot_report_zero_tax_for_premiums_alone():
    result = run(case([event("premium", 20)], ordinary_personal_contract_confirmed=False))
    assert result["annual"][0]["tax_change"] is None
    assert result["rows"][0]["federal_ordinary_income"] is None
    assert result["external_cash"] == -20
