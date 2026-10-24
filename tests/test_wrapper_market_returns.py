"""Two percent monthly stays invested; wrapper yield is not deposited as household cash.

The old entered 50% IRA event is replaced only in the compiled copy. $100k IRA
and $30k 529 compound to $126,824.17 and $38,047.26 with monthly cent rounding;
$100k household cash is unchanged. No fake taxable account is required.
"""

from decimal import Decimal

import pytest

from tests.wrapper_market_cases import flat
from wealthlab.markets.household_run import run
from wealthlab.markets.paths import generate


@pytest.fixture(scope="module")
def result():
    case, market, binding = flat()
    original = case.model_dump_json()
    outcome = run(case, generate(market), binding)
    return case, original, outcome


def test_actual_proxy_return_conserves_household_assets_without_extra_cash(result):
    _, _, outcome = result
    rows = outcome["details"][0]["rows"]
    assert rows[-1]["account_balances"]["retirement"] == Decimal("126824.17")
    assert rows[-1]["account_balances"]["college"] == Decimal("38047.26")
    assert rows[-1]["closing_cash"] == 100000
    assert rows[-1]["net_wealth"] == Decimal("264871.43")
    assert sum(r["market_cash_yield"] for r in rows) == 0


def test_source_and_issuer_inventory_are_not_replaced_by_assumed_holdings(result):
    case, original, outcome = result
    assert case.model_dump_json() == original
    assert outcome["household"]["ira_plan"]["returns"][0]["rate"] == "0.5"
    assert outcome["outcomes"][0]["max_security_weight"] is None
    assert not outcome["outcomes"][0]["issuer_concentration_complete"]
    assert outcome["details"][0]["rows"][-1]["market_factor_values"]["portfolio"] > 160000
