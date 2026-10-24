"""Actual policies share the household book, swept cash and funding-sale history.

The first 50% target sells 495 of 1,000 $100 shares: $50,500 stock remains
against $50,500 household cash. A later identical target sells nothing even
though the lot book itself has swept away all its cash. Supplied $999 quotes
are not the realized market marks and cannot dictate the household execution.
"""

from tests.household_policy_cases import staged, targets
from wealthlab.markets.household_run import run
from wealthlab.markets.paths import generate


def test_concentration_target_counts_cash_swept_to_the_household():
    case, market, binding = targets()
    original = case.model_dump_json()
    result = run(case, generate(market), binding)
    rows = result["details"][0]["rows"]
    decisions = rows[-1]["lot_audit"]["sale_decisions"]
    assert [d["sold_units"] for d in decisions] == [495, 0]
    assert case.model_dump_json() == original
    assert rows[-1]["net_wealth"] == 101000
    assert rows[-1]["closing_cash"] == rows[-1]["account_balances"]["brokerage"] == 50500
    assert rows[-1]["lot_audit"]["trades"][0]["price"] == "100.00000000"


def test_cumulative_original_share_targets_include_prior_funding_sales():
    case, market, binding = staged()
    rows = run(case, generate(market), binding)["details"][0]["rows"]
    decisions = rows[-1]["lot_audit"]["sale_decisions"]
    assert [d["sold_units"] for d in decisions] == [10, 0]
    assert rows[0]["lot_funding_proceeds"] == 1000
    assert rows[1]["lot_funding_proceeds"] == 1000
    assert sum(r["essential"] for r in rows) == 48000
    assert rows[-1]["net_wealth"] == 53000


def test_policy_commission_reduces_capital_once():
    from wealthlab.household.scenario import Scenario

    case, market, binding = targets()
    data = case.model_dump(mode="json")
    data["lot_plan"]["case"]["sale_policies"][0]["commission"] = "1"
    rows = run(Scenario.model_validate(data), generate(market), binding)["details"][0]["rows"]
    assert rows[-1]["net_wealth"] == 100999
    assert rows[-1]["closing_cash"] == rows[-1]["account_balances"]["brokerage"]
    assert len(rows[-1]["lot_audit"]["trades"]) == 1
