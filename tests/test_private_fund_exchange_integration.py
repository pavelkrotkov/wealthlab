"""The composite must retain both audits, settle each actual asset once and aggregate one return."""

from private_fund_exchange_cases import combined

from wealthlab.household.projection import project


def test_mixed_private_and_exchange_funds_use_one_wallet_and_one_annual_return():
    case = combined()
    source = case.model_dump_json()
    rows = project(case)
    final = rows[-1]
    assert final["annual_tax"]["federal"]["agi"] == 100000
    assert final["annual_tax"]["new_jersey"]["gross_income"] == 80000
    assert final["net_wealth"] == 230000 - final["annual_tax"]["total_liability"]
    assert final["sleeve_audit"][-1]["fund_complete_liquidation"]
    assert final["exchange_fund_audit"]["remaining_lots"] == []
    assert (final["account_balances"]["exchange"], final["account_balances"]["sleeve"]) == (0, 0)
    assert case.model_dump_json() == source
