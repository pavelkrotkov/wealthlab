"""Contract and tax baselines reject economically inconsistent paths."""

import pytest

from tests.life_contract_cases import case, event
from wealthlab.products.life_contract import run
from wealthlab.products.life_contract_example import synthetic
from wealthlab.products.life_contract_inputs import LifeContractCase


@pytest.mark.parametrize(
    "change, message",
    [
        ("terminal_value", "before termination"),
        ("duplicate_value", "unique and ordered"),
        ("unresolved_event", "resolved"),
        ("invalid_stop", "precede issue"),
        ("wrong_baseline_year", "match its tax year"),
    ],
)
def test_supplied_history_and_annual_year_must_correspond(change, message):
    data = synthetic().model_dump(mode="json")
    contract = data["contract"]
    if change == "terminal_value":
        contract["values"][0]["date"] = "2025-07-01"
    if change == "duplicate_value":
        contract["values"] *= 2
    if change == "unresolved_event":
        contract["events"][0]["provenance"] = "unresolved"
    if change == "invalid_stop":
        contract["stop_funding_date"] = "1999-01-01"
    if change == "wrong_baseline_year":
        data["annual_cases"]["2025"]["policy"]["year"] = 2026
    with pytest.raises(ValueError, match=message):
        run(LifeContractCase.model_validate(data))


def test_mec_impossible_cash_distribution_and_unrelated_nj_income_are_rejected():
    with pytest.raises(ValueError, match="pre-receipt"):
        run(case([event("withdrawal", 200, cash_value_before="150")], federal_status="mec"))
    flow = event("premium", 1)
    flow["nj_ordinary_income"] = "1"
    with pytest.raises(ValueError, match="overrides"):
        run(case([flow]))


def test_missing_retirement_date_and_opening_loan_do_not_invent_values():
    data = synthetic().model_dump(mode="json")
    data["retirement_date"] = None
    data["contract"]["values"][0]["gross_cash_value"] = "120000"
    result = run(LifeContractCase.model_validate(data))
    assert result["premiums_from_retirement"] is None
    assert result["values"][0]["loan_contract_review_required"]
    assert result["values"][0]["net_cash_value"] is None


def test_unresolved_opening_source_is_rejected():
    with pytest.raises(ValueError, match="opening snapshot"):
        case(provenance="unresolved")
