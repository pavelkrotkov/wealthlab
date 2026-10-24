"""Custodian arrears reduce wealth before payment and precede cash withdrawals."""

from wealthlab.retirement.hsa_investment_example import synthetic
from wealthlab.retirement.hsa_investment_inputs import HSAInvestments
from wealthlab.retirement.hsa_investments import run


def test_unpaid_custody_fee_remains_a_liability_until_actual_sale_proceeds_pay_it():
    data = synthetic().model_dump(mode="json")
    data["case"]["accounts"][0]["cash"] = "0"
    data["case"].update(trades=[], distributions=[])
    data["cash_targets"] = []
    owing = run(HSAInvestments.model_validate(data))
    assert owing["fee_summary"]["cash_owed"] == 50
    assert owing["net_wealth"] == 10950
    assert owing["cash_by_account"]["hsa"] == 0
    data["cash_targets"] = [
        dict(id="need", provenance="assumption", date="2026-12-31", account_id="hsa", amount=500)
    ]
    paid = run(HSAInvestments.model_validate(data))
    assert paid["cash_by_account"]["hsa"] == 500
    assert paid["fee_summary"]["cash_owed"] == 0
    assert paid["net_wealth"] == 10948
