"""Locked wealth cannot pay consumption or current taxes; early exits use actual cash once.

The matched liquid basket and locked fund start with identical household wealth.
An attempted redemption cannot fund a bill until the specified contract permits it.
"""

from datetime import date

from exchange_fund_cases import change, flat

from wealthlab.household.projection import project
from wealthlab.products.exchange_fund_compare import compare
from wealthlab.products.exchange_fund_example import request


def test_early_denial_preserves_locked_value_while_liquid_direct_basket_funds_spending():
    def configure(data):
        data["accounts"][0]["balance"] = "0"
        data["expenses"] = [
            dict(
                id="bill",
                provenance="illustration",
                start="2026-01-01",
                end="2026-02-01",
                currency="USD",
                monthly_amount="10000",
                annual_growth=0,
                category="essential",
            )
        ]
        data["exchange_fund_plan"]["requests"] = [
            request("early", date(2026, 1, 31), "redeem"),
            request("sell", date(2026, 1, 31), "sell_liquid"),
        ]

    result = compare(change(flat(), configure))
    locked = result["rows"]["exchange"][0]
    direct = result["rows"]["direct_sale"][0]
    assert locked["funding_shortfall"] == 10000
    assert locked["exchange_locked_value"] == 100000
    assert locked["exchange_denied_redemptions"] == 1
    assert direct["funding_shortfall"] == 0
    assert direct["closing_cash"] == 90000
    assert result["outcomes"]["exchange"]["funding_failure_months"] == 1


def test_early_cash_fee_and_supplied_recognition_use_one_cash_source():
    def configure(data):
        plan = data["exchange_fund_plan"]
        early = request("early", date(2026, 1, 31), "redeem")
        early["early_tax_confirmed"] = True
        early["early_tax"]["federal"] = dict(long_term="78000")
        early["early_tax"]["new_jersey"] = dict(dispositions="68000")
        plan.update(early_redemption="cash_with_supplied_tax", requests=[early])

    rows = project(change(flat(), configure))
    assert rows[0]["exchange_early_cash"] == 98000
    assert rows[0]["exchange_fees"] == 2000
    assert rows[0]["closing_cash"] == 128000
    assert rows[0]["account_balances"]["exchange"] == 0
    assert rows[-1]["annual_tax"]["federal"]["agi"] == 78000
    assert rows[-1]["net_wealth"] == 128000 - rows[-1]["annual_tax"]["total_liability"]
