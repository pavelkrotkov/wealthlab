"""Salary reductions enter one actual invested HSA cash account and settle custodian fees."""

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.retirement.hsa_invested_example import synthetic as invested
from wealthlab.retirement.hsa_payroll_example import synthetic


def test_salary_contributions_and_reimbursements_do_not_duplicate_investment_cash():
    data = synthetic().model_dump(mode="json")
    investment_plan = invested().hsa_plan.investments.model_dump(mode="json")
    data["accounts"][-1].update(id="hsa", balance="10100")
    plan = data["hsa_plan"]
    for row in [*plan["contributions"], *plan["payroll"]["orders"]]:
        row["destination"] = "hsa"
    plan["withdrawals"][0]["source"] = "hsa"
    plan.update(
        investments=investment_plan,
        cash_only_accounts_and_complete_context_confirmed=False,
        cash_accounts_outside_investment_book_confirmed=True,
        investment_income_excluded_from_other_inputs_confirmed=True,
    )
    rows = project(Scenario.model_validate(data))
    audit = rows[-1]["hsa_audit"]["investments"]
    assert audit["cash_by_account"]["hsa"] == 5150
    assert audit["fee_summary"]["cash_paid"] == 50
    assert rows[-1]["account_balances"]["hsa"] == 16150
    assert rows[-1]["net_wealth"] == 231650 - rows[-1]["annual_tax"]["total_liability"]
    assert rows[-1]["annual_tax"]["new_jersey"]["gross_income"] == 96600
