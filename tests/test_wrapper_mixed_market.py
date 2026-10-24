"""A shared factor may drive taxable shares and wrapper proxies without duplicating cash yield."""

from decimal import Decimal

from wealthlab.household.scenario import Scenario
from wealthlab.markets.household_example import synthetic as taxable
from wealthlab.markets.household_inputs import HouseholdBinding
from wealthlab.markets.household_run import run
from wealthlab.markets.paths import generate
from wealthlab.markets.wrapper_example import synthetic


def test_mixed_accounts_keep_wrapper_returns_out_of_taxable_yield_cash():
    household, market, binding = synthetic()
    lots, _, other = taxable()
    data = household.model_dump(mode="json")
    data["accounts"].append(lots.accounts[1].model_dump(mode="json"))
    data["lot_plan"] = lots.lot_plan.model_dump(mode="json")
    plan = binding.model_dump(mode="json")
    plan["securities"] = [dict(other.securities[0].model_dump(mode="json"), factor="portfolio")]
    result = run(
        Scenario.model_validate(data), generate(market), HouseholdBinding.model_validate(plan)
    )
    rows = result["details"][0]["rows"]
    dividends = sum(r["market_cash_yield"] for r in rows[:12])
    assert rows[0]["market_cash_yield"] == Decimal("166.67")
    assert rows[11]["annual_tax"]["federal"]["agi"] == 30000 + dividends
    assert set(rows[-1]["market_security_values"]) == {"stock"}
    assert not result["outcomes"][0]["issuer_concentration_complete"]
    assert (
        rows[-1]["market_factor_values"]["portfolio"] > rows[-1]["market_security_values"]["stock"]
    )
