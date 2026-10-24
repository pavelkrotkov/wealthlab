"""Funding uses actual lots; generated receipts share owner/year limits.

Direct HSA payment reduces a bill before the permitted lot-sale quote.
New paid cash is usable only after healthcare funding, including December's
cash payment before the annual receipt audit is captured.
"""

from medical_bill_cases import data

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.portfolio.household_example import plan as lot_plan


def test_actual_lot_sale_funds_the_remaining_bill_without_phantom_cash():
    value = data()
    value["accounts"].append(
        dict(
            id="brokerage",
            provenance="assumption",
            owner="person_a",
            wrapper="taxable",
            currency="USD",
            balance=100000,
            monthly_fee=0,
        )
    )
    scenario = Scenario.model_validate(value)
    value["lot_plan"] = lot_plan(scenario)
    first = project(Scenario.model_validate(value))[0]
    assert first["lot_funding_proceeds"] == 2000
    assert first["medical_provider_paid"] == 3000
    assert first["medical_cash_paid"] == 3000
    assert first["medical_owed"] == 0
    assert not first["funding_failure"]
    assert first["net_wealth"] == 104000 - 6000 - 1


def test_december_cash_payment_precedes_the_completed_receipt_audit():
    value = data(cash=6000, hsa_amount=0, hsa_source=None, date="2026-12-15")
    value["hsa_plan"]["withdrawals"] = [
        dict(
            id="next_january",
            provenance="assumption",
            date="2027-01-01",
            source="cash_hsa",
            amount=3000,
            mode="qualified_only",
            receipt_ids=["care"],
        )
    ]
    rows = project(Scenario.model_validate(value))
    annual = rows[-1]["hsa_audit"]["years"]
    assert [r["remaining_receipts"]["care"] for r in annual] == [6000, 3000]
    assert rows[11]["medical_cash_paid"] == 6000
    assert rows[12]["hsa_withdrawal_cash"] == 3000
    assert rows[-1]["net_wealth"] == 3000
