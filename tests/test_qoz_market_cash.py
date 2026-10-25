"""Actual source sales, inclusion and settlement conserve household capital."""

from tests.qoz_market_cases import flat
from wealthlab.markets.household_run import run


def test_flat_native_source_gain_and_final_tax_cash_reconcile_once():
    case, batch, binding = flat()
    original = case.model_dump_json()
    result = run(case, batch, binding)
    rows = result["details"][0]["rows"]
    source = rows[-1]["lot_audit"]["disposals"][0]
    assert case.model_dump_json() == original
    assert (source["trade_id"], source["date"], source["proceeds"]) == (
        "source_sale",
        "2026-01-31",
        100000,
    )
    assert (source["federal_gross_gain"], source["nj_gross_gain"]) == (80000, 70000)
    assert rows[0]["qoz_call_paid"] == 80000
    assert rows[-1]["qoz_original_gain_included"] == rows[-1]["qoz_settlement_cash"] == 80000
    # $105k initial wealth +$72k wages -($7,953 federal +$5,508 payroll +$4,960 NJ).
    assert rows[-1]["annual_tax"]["total_liability"] == 18421
    assert rows[-1]["closing_cash"] == rows[-1]["net_wealth"] == 158579


def test_post_call_growth_is_actual_appreciation_with_current_holding_period_tax():
    shocks = [dict(name="post-call growth", month=1, mark_shocks=dict(qof_assets=0.1))]
    case, batch, binding = flat(shocks=shocks)
    final = run(case, batch, binding)["details"][0]["rows"][-1]
    # $8k earned in February remains a short-term QOF-stock gain at December sale.
    # Federal $10,113 +payroll $5,508 +NJ $5,402 = $21,023; no inherited stock clock.
    assert final["qoz_settlement_cash"] == 88000
    assert final["annual_tax"]["total_liability"] == 21023
    assert final["annual_tax"]["federal"]["agi"] == 160000
    assert final["closing_cash"] == final["net_wealth"] == 163977


def test_new_call_does_not_earn_the_already_observed_call_month_return():
    shocks = [dict(name="before subscription", month=0, mark_shocks=dict(qof_assets=0.5))]
    case, batch, binding = flat(shocks=shocks)
    rows = run(case, batch, binding)["details"][0]["rows"]
    assert rows[0]["qoz_entity_equity"] == rows[0]["qoz_entity_asset_value"] == 80000
    assert rows[-1]["qoz_settlement_cash"] == 80000
    assert rows[-1]["closing_cash"] == 158579
