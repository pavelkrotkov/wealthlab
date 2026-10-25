"""Actual plan receipts and cash-funded ordinary deposits coexist in one dynamic IRA book."""

from decimal import Decimal

from wealthlab.household.example import synthetic as working
from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.retirement.ira_deposit_household_example import template as deposit_template
from wealthlab.retirement.workplace_rollover_example import synthetic
from wealthlab.tax.projection_example import template as tax_template


def contribution_case():
    data = synthetic().model_dump(mode="json")
    salary = working().incomes[0].model_dump(mode="json")
    salary.update(monthly_amount=5000, end="2028-01-01", stop_at_retirement=False)
    data["incomes"] = [salary]
    scenario = Scenario.model_validate(data)
    plan = deposit_template(scenario)
    plan["orders"] = [
        dict(
            id="ordinary_deposit",
            provenance="illustration",
            date="2026-04-15",
            owner="person_a",
            destination="ira",
            kind="traditional_ira",
            amount=3000,
        )
    ]
    data["ira_plan"]["contributions"] = plan
    data["tax_plan"] = tax_template(scenario).model_dump(mode="json")
    return Scenario.model_validate(data)


def test_rollover_and_ordinary_deposit_keep_separate_basis_deduction_and_cash():
    rows = project(contribution_case())
    result = rows[11]["ira_annual_reconciliation"]
    assert result["incoming_rollover_value"] == 80000
    assert result["contribution_owners"][0]["traditional_ira"] == 3000
    assert result["contribution_owners"][0]["federal_ira_deduction"] == 3000
    assert result["owners"][0]["federal_ira_basis"] == 0
    assert result["owners"][0]["nj_ira_basis"] == Decimal("2516.13")
    assert rows[-1]["account_balances"]["ira"] == 78000
