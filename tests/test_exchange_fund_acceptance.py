"""Rejected contributions retain source shares; market locks preserve unavailable assets."""

from decimal import Decimal

from exchange_fund_cases import change, flat

from wealthlab.household.projection import project


def test_rejected_contribution_preserves_actual_source_stock_without_fund_fees():
    case = change(flat(), lambda d: d["exchange_fund_plan"].update(accepted=False))
    rows = project(case)
    assert rows[-1]["exchange_acceptance_denied"]
    assert rows[-1]["account_balances"]["exchange"] == 100000
    assert rows[-1]["net_wealth"] == 130000
    assert rows[-1]["exchange_fund_audit"]["remaining_lots"][0]["id"] == "original_lot"


def test_liquidity_lock_blocks_even_a_requested_post_contract_release_and_sale():
    def configure(data):
        data["exchange_fund_plan"]["observations"][-1]["locked"] = True

    rows = project(change(flat(), configure))
    assert rows[-1]["exchange_denied_redemptions"] == 2
    assert rows[-1]["exchange_locked_value"] == Decimal("100000")
    assert rows[-1]["closing_cash"] == 30000
