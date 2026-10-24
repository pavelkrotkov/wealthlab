"""A real tuition bill survives an empty 529; cash and shortfalls stay distinct.

Fallback is spending, not a second distribution or a new source of earnings.
The same bill contributes to education demand once, and optional unfilled
savings requests do not become mandatory spending failures.
"""

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.retirement.education_household_example import synthetic


def cash_only_data():
    data = synthetic().model_dump(mode="json")
    data["hsa_plan"] = None
    data["ira_plan"] = None
    data["education_plan"].update(contributions=[], returns=[])
    data["accounts"][-1]["balance"] = "1000"
    data["education_plan"]["accounts"][0]["contribution_basis"] = "500"
    return data


def test_cash_pays_only_the_tuition_not_paid_by_the_wrapper():
    data = cash_only_data()
    data["accounts"][0]["balance"] = "100000"
    rows = project(Scenario.model_validate(data))
    assert sum(r["education_wrapper_paid"] for r in rows) == 1000
    assert sum(r["education_cash_fallback"] for r in rows) == 23000
    assert sum(r["education"] for r in rows) == 24000
    assert rows[-1]["account_balances"]["college"] == 0
    assert sum(r["education_unfunded"] for r in rows) == 0


def test_no_cash_or_wrapper_money_reports_one_unpaid_tuition_bill():
    data = cash_only_data()
    data.update(incomes=[], expenses=[])
    data["tax_plan"]["income_rules"] = []
    data["accounts"] = [a for a in data["accounts"] if a["wrapper"] in {"cash", "education"}]
    for account in data["accounts"]:
        account["balance"] = "0"
    data["education_plan"]["accounts"][0]["contribution_basis"] = "0"
    rows = project(Scenario.model_validate(data))
    assert sum(r["education_unfunded"] for r in rows) == 24000
    assert sum(r["funding_shortfall"] for r in rows) == 24000
    assert sum(r["education_cash_fallback"] for r in rows) == 0
    assert sum(bool(r["funding_failure"]) for r in rows) == 2


def test_high_actual_nj_income_removes_the_forecast_deduction():
    data = synthetic().model_dump(mode="json")
    data.update(hsa_plan=None, ira_plan=None)
    data["incomes"][0].update(monthly_amount="20000", stop_at_retirement=False)
    rows = project(Scenario.model_validate(data))
    audit = rows[-1]["education_audit"]["years"]
    assert [y["njbest_funded_contributions"] for y in audit] == [6000, 6000]
    assert [y["njbest_potential_deduction"] for y in audit] == [0, 0]


def test_unfunded_savings_request_does_not_create_a_deduction_or_spending_failure():
    data = synthetic().model_dump(mode="json")
    data.update(hsa_plan=None, ira_plan=None, incomes=[], expenses=[])
    data["accounts"][0]["balance"] = "0"
    data["tax_plan"]["income_rules"] = []
    data["education_plan"].update(tuition=[], returns=[])
    rows = project(Scenario.model_validate(data))
    assert sum(r["education_deposits"] for r in rows) == 0
    assert sum(r["education_unfilled_deposits"] for r in rows) == 12000
    assert not any(r["funding_failure"] for r in rows)
    assert [y["njbest_potential_deduction"] for y in rows[-1]["education_audit"]["years"]] == [0, 0]


def test_total_market_loss_carries_unclosed_basis_into_the_next_year():
    data = cash_only_data()
    data["accounts"][0]["balance"] = "100000"
    plan = data["education_plan"]
    plan["contributions"] = [
        dict(
            id="later_deposit",
            provenance="illustration",
            date="2027-02-01",
            destination="college",
            amount="6000",
        )
    ]
    plan["returns"] = [
        dict(
            id="total_loss",
            provenance="illustration",
            date="2026-06-01",
            account_id="college",
            rate="-1",
        )
    ]
    rows = project(Scenario.model_validate(data))
    audit = rows[-1]["education_audit"]["years"]
    assert audit[0]["contribution_basis"]["college"] == 500
    assert audit[1]["closed_account_loss_basis"] == 500
    assert audit[1]["contribution_basis"]["college"] == 0
    assert audit[1]["annual_tax_groups"][0]["federal_taxable_earnings"] == 0
