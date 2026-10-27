"""Four products close through actual cash; contracts remain shared across retirement policies.

The independent identity is340000opening capital less48000living expenses and
one dollar ordinary-lot commission. Neither fund redemption, exchange release
nor policy surrender can add its principal a second time.
"""

from decimal import Decimal

import pytest
from optimization_product_cases import case

from wealthlab.optimization.compile import compile_candidate
from wealthlab.optimization.product_exits import complete
from wealthlab.optimization.search import search


@pytest.fixture(scope="module")
def result():
    return search(case())


def test_all_native_exits_reconcile_cash_and_holdout_without_duplicate_product_capital(result):
    assert result["candidates"][0]["median_real_after_tax_exit_wealth"] == 291999
    assert result["held_out"]["assessment"]["eligible"]
    rows = result["selected_training"]["details"][0]["rows"]
    assert rows[-1]["closing_cash"] == 291999
    assert all(value == 0 for key, value in rows[-1]["account_balances"].items() if key != "cash")
    assert complete(case().household, rows[-1])


def test_each_product_receipt_reaches_the_household_once(result):
    rows = result["selected_training"]["details"][0]["rows"]
    assert sum(r["sleeve_redemptions"] for r in rows) == 10000
    assert sum(r.get("liquidation_cash", 0) for r in rows[-1]["sleeve_audit"]) == 10000
    assert sum(r["exchange_sale_cash"] for r in rows) == 10000
    assert sum(r["life_cash_received"] for r in rows) == 10000
    assert complete(case().household, rows[-1])


def test_native_audit_preserves_actual_margin_debt_and_collateral_closure(result):
    rows = result["selected_training"]["details"][0]["rows"]
    states = {
        r["account_id"]: r["exit_state"] for r in rows[-1]["sleeve_audit"] if "exit_state" in r
    }
    assert states["margin_sleeve"]["financing_loan"] == 0
    assert states["margin_sleeve"]["short_collateral"] == 0


def test_native_private_liquidation_closes_the_investor_interest_and_basis(result):
    audit = result["selected_training"]["details"][0]["rows"][-1]["sleeve_audit"]
    fund = next(
        r["exit_state"] for r in audit if r["account_id"] == "private_fund" and "exit_state" in r
    )
    assert fund["investor_interest_closed"]
    assert fund["settlements"] == fund["unrecognized_future_events"] == []
    assert fund["outside_basis"] == dict(federal=Decimal(0), new_jersey=Decimal(0))


def test_policy_compilation_preserves_every_product_term_and_tax_assumption():
    profile = case()
    before = profile.model_dump_json()
    early, _ = compile_candidate(profile, [profile.dimensions[0].choices[0]])
    later, _ = compile_candidate(profile, [profile.dimensions[0].choices[1]])
    for key in ("sleeve_plan", "exchange_fund_plan", "life_plan", "accounts", "tax_plan"):
        assert getattr(early, key) == getattr(later, key) == getattr(profile.household, key)
    assert before == profile.model_dump_json()
