"""Dealing locks preserve asset value and statutory inclusion while restricting real cash."""

from tests.qoz_market_cases import flat
from wealthlab.household.scenario import Scenario
from wealthlab.markets.household_run import run


def test_locked_year_end_inclusion_cannot_spend_an_unreceived_stock_sale():
    case, batch, binding = flat(
        shocks=[dict(name="sale lock", month=11, lock_months=dict(qof_assets=1))]
    )
    final = run(case, batch, binding)["details"][0]["rows"][-1]
    assert final["qoz_original_gain_included"] == 80000
    assert final["qoz_settlement_cash"] == 0
    assert final["qoz_nav"] == 80000
    assert final["annual_tax"]["total_liability"] == 18421
    assert final["closing_cash"] == 78579
    assert final["net_wealth"] == 158579


def test_unlock_next_month_executes_and_deposits_stock_sale_once():
    case, batch, binding = flat(
        13, [dict(name="sale lock", month=11, lock_months=dict(qof_assets=1))]
    )
    rows = run(case, batch, binding)["details"][0]["rows"]
    assert rows[11]["qoz_settlement_cash"] == 0
    assert rows[12]["qoz_settlement_cash"] == 80000
    assert rows[-1]["qoz_nav"] == rows[-1]["qoz_receivable"] == rows[-1]["qoz_internal_debt"] == 0
    # One further $6k wage receipt less $459 payroll, without paying prior tax twice.
    assert rows[-1]["closing_cash"] == 164120


def test_supplied_dealing_lock_is_retained_even_when_generated_factor_is_unlocked():
    case, batch, binding = flat()
    data = case.model_dump(mode="json")
    data["qoz_plan"]["observations"][-1]["locked"] = True
    final = run(Scenario.model_validate(data), batch, binding)["details"][0]["rows"][-1]
    assert final["qoz_settlement_cash"] == 0
    assert final["qoz_nav"] == 80000
    assert final["qoz_audit"]["terms"]["observations"][-1]["locked"]
