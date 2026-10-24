"""Earlier elections cannot consume unpaid bills or later HSA deposits.

Late employer funding may pay the bill at the disclosed month-end retry;
it must not retrospectively create an earlier distribution or receipt.
Persistent unpaid liabilities remain failures without repeatedly adding cost.
"""

from datetime import date

from medical_bill_cases import case, data

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario


def test_outstanding_bill_cannot_hide_behind_a_later_month_without_new_bills():
    rows = project(case(cash=0, hsa=0))
    assert rows[0]["medical_bills_unfunded"] == 6000
    assert rows[1]["medical_bills_unfunded"] == 0
    assert rows[1]["medical_owed"] == 6000
    assert rows[1]["funding_failure"]
    assert rows[-1]["net_wealth"] == -6000
    assert sum(r["funding_shortfall"] for r in rows) == 6000


def test_later_hsa_cash_pays_at_actual_retry_without_creating_early_receipts():
    value = data(cash=0, hsa=0, hsa_amount=3000)
    value["hsa_plan"]["contributions"] = [
        dict(
            id="late_employer",
            provenance="assumption",
            date="2026-01-20",
            destination="cash_hsa",
            source="direct_employer",
            amount=5000,
        )
    ]
    value["hsa_plan"]["withdrawals"] = [
        dict(
            id="too_early",
            provenance="assumption",
            date="2026-01-14",
            source="cash_hsa",
            amount=1000,
            mode="qualified_only",
            receipt_ids=["care"],
        )
    ]
    rows = project(Scenario.model_validate(value))
    orders = rows[-1]["hsa_audit"]["orders"]
    assert orders[0]["funded"] == 0
    assert orders[-1]["date"] == date(2026, 1, 31)
    assert rows[0]["medical_provider_paid"] == 3000
    assert rows[0]["medical_owed"] == 3000
    assert rows[0]["closing_cash"] == 0
    assert rows[-1]["hsa_audit"]["receipt_remaining"] == {"care": 0}


def test_care_before_establishment_cannot_use_a_qualified_direct_election():
    rows = project(case(incurred="2019-01-01"))
    assert sum(r["medical_provider_paid"] for r in rows) == 0
    assert rows[0]["medical_cash_paid"] == 1000
    assert rows[0]["medical_owed"] == 5000
    assert rows[-1]["account_balances"]["cash_hsa"] == 3000


def test_a_due_but_unpaid_bill_cannot_back_a_same_month_reimbursement():
    value = data(cash=6000, hsa_amount=0, hsa_source=None)
    value["hsa_plan"]["withdrawals"] = [
        dict(
            id="unpaid_claim",
            provenance="assumption",
            date="2026-01-20",
            source="cash_hsa",
            amount=3000,
            mode="qualified_only",
            receipt_ids=["care"],
        )
    ]
    rows = project(Scenario.model_validate(value))
    assert rows[0]["hsa_withdrawal_cash"] == 0
    assert rows[0]["hsa_unfilled_requests"] == 3000
    assert rows[0]["medical_cash_paid"] == 6000
    assert rows[-1]["account_balances"]["cash_hsa"] == 3000
    assert rows[-1]["hsa_audit"]["receipt_remaining"] == {"care": 6000}
