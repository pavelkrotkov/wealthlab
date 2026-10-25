"""All funded HSA sources consume the same annual eligible owner contribution room."""

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.retirement.hsa_payroll_example import synthetic


def test_shared_hsa_annual_room_blocks_optional_salary_elections_without_excess():
    data = synthetic().model_dump(mode="json")
    for order in data["hsa_plan"]["payroll"]["orders"]:
        order["amount"] = "1000"
    rows = project(Scenario.model_validate(data))
    audit = rows[-1]["hsa_audit"]
    assert sum(r["hsa_payroll_contributions"] for r in rows) == 7250
    assert audit["years"][0]["employer_reported_contributions"] == 7750
    assert audit["years"][0]["personal_federal_deduction"] == 1000
    assert sum(r["hsa_payroll_unfilled"] for r in rows) == 4750
    assert rows[-1]["account_balances"]["cash_hsa"] == 8250
