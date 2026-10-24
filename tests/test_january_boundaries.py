"""Partial replacements and capital carry retain original-year character.

Only replacement shares defer the December loss. An unused allowed loss
first offsets the original year's gain, then supplies the statutory ordinary
allowance and next year's opening carry; January gains consume that carry.
"""

from decimal import Decimal

from tests.january_ira_cases import case as ira_case
from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.portfolio.january_example import synthetic


def test_partial_january_replacement_allows_only_the_unmatched_loss():
    data = synthetic().model_dump(mode="json")
    trade = dict(data["lot_plan"]["case"]["trades"][0])
    trade.update(id="partial_buy", date="2027-01-10", action="buy", quantity="4", selection="fifo")
    data["lot_plan"]["case"]["trades"].append(trade)
    rows = project(Scenario.model_validate(data))
    audit = rows[-1]["lot_audit"]
    assert audit["disposals"][0]["federal_wash_deferred"] == 160
    final = audit["return_reconciliations"][0]["final_result"]["federal"]
    assert final["agi"] == 59760
    assert rows[15]["tax_refund_received"] == Decimal("28.80")


def test_preserved_nondeductible_election_is_not_silently_rewritten():
    data = ira_case().model_dump(mode="json")
    data["incomes"][0]["monthly_amount"] = "9000"
    for year in data["ira_plan"]["contributions"]["years"]:
        person = year["contributors"][0]
        person.update(covered_by_workplace_plan=True, traditional_ira_magi="160000")
    rows = project(Scenario.model_validate(data))
    audit = rows[-1]["lot_audit"]["return_reconciliations"][0]
    assert audit["ira_eligibility"]["traditional_ira_magi"] < 149000
    owners = rows[11]["ira_annual_reconciliation"]["contribution_owners"]
    assert owners[0]["federal_ira_deduction"] == 0
    assert owners[0]["new_federal_ira_basis"] == 3000
    assert (
        audit["final_result"]["federal"]["agi"] == audit["ira_eligibility"]["traditional_ira_magi"]
    )


def test_original_year_unused_loss_carries_into_january_gain():
    data = synthetic().model_dump(mode="json")
    data["lot_plan"]["case"]["trades"][0]["quantity"] = "600"
    data["tax_plan"]["events"].append(
        dict(
            date="2027-01-10",
            description="Synthetic subsequent-year gain allocation",
            cash_received="0",
            federal=dict(long_term="10000"),
            new_jersey=dict(dispositions="10000"),
        )
    )
    rows = project(Scenario.model_validate(data))
    original = rows[-1]["lot_audit"]["return_reconciliations"][0]["final_result"]["federal"]
    assert original["agi"] == 57000
    assert original["long_carry"] == 21000
    assert rows[12]["annual_tax"]["federal"]["agi"] == -3000
    # No ordinary income in 2027: its apparent $3k deduction does not use carry.
    assert rows[-1]["annual_tax"]["federal"]["long_carry"] == 11000
