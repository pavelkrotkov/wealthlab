"""Dated cash receipts pay assessed arrears before optional HSA deposits."""

from datetime import date
from decimal import Decimal

from wealthlab.household.funding import Wallet
from wealthlab.household.scenario import Scenario
from wealthlab.retirement.hsa_household import Ledger
from wealthlab.retirement.hsa_household_example import synthetic
from wealthlab.tax.projection_ledger import TaxLedger


def test_new_receipt_cannot_bypass_prior_tax_and_fund_an_optional_deposit():
    data = synthetic().model_dump(mode="json")
    data.update(ira_plan=None, incomes=[])
    data["accounts"][0]["balance"] = "0"
    data["tax_plan"]["income_rules"] = []
    data["tax_plan"]["events"] = [
        dict(
            date="2026-01-01",
            description="Synthetic cash receipt",
            cash_received="500",
            federal={},
            new_jersey={},
        )
    ]
    deposit = data["hsa_plan"]["contributions"][0]
    deposit.update(date="2026-01-01", amount="400")
    data["hsa_plan"].update(contributions=[deposit], withdrawals=[], interest=[])
    case = Scenario.model_validate(data)
    wallet, hsa = Wallet(case), Ledger(case)
    tax = TaxLedger(case.tax_plan, case)
    tax.outstanding["federal"] = Decimal(500)
    row = tax.month(
        {}, wallet, date(2026, 1, 1), date(2026, 2, 1), Decimal(0), receipt_hook=hsa.after_receipts
    )
    assert row["prior_tax_paid"] == 500
    assert hsa.book["personal"] == 0
    assert tax.owed == 0
