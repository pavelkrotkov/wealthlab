"""Receipt deductions, cash priority and immutable exports retain their meaning.

The same paid receipt spans two annual HSA books, so a prior deduction must
reduce total qualified capacity rather than just the first year's withdrawal.
Moving reimbursement between household cash and the HSA cannot change wealth.
Personal deposits spend actual available cash: a failed February request must
not acquire a deduction or become a March deposit when wages finally arrive.
The serialized scenario is a reusable input, never a mutable projection ledger.
"""

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.retirement.hsa_household_example import synthetic


def test_prior_federal_deduction_removes_that_portion_from_qualified_capacity():
    data = synthetic().model_dump(mode="json")
    data["hsa_plan"]["medical_receipts"][0]["deducted_federally"] = "1000"
    rows = project(Scenario.model_validate(data))
    assert sum(r["hsa_withdrawal_cash"] for r in rows) == 2000
    assert rows[-1]["account_balances"]["cash_hsa"] == 18300
    assert rows[-1]["net_wealth"] == 155243


def test_unfunded_personal_deposit_has_no_deduction_and_is_not_retried():
    data = synthetic().model_dump(mode="json")
    data["end"] = "2027-01-01"
    data["ira_plan"] = None
    data["accounts"][0]["balance"] = "0"
    data["expenses"] = []
    data["incomes"][0]["start"] = "2026-03-01"
    data["tax_plan"]["cases"] = data["tax_plan"]["cases"][:1]
    plan = data["hsa_plan"]
    plan["years"] = plan["years"][:1]
    for key in ("contributions", "withdrawals", "interest"):
        plan[key] = [r for r in plan[key] if r["date"].startswith("2026")]
    rows = project(Scenario.model_validate(data))
    assert sum(r["hsa_personal_contributions"] for r in rows) == 0
    assert rows[-1]["hsa_audit"]["years"][0]["personal_federal_deduction"] == 0
    assert rows[-1]["annual_tax"]["federal"]["agi"] == 50000
