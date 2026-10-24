"""Realized CPI affects later spending, while an unobserved crash cannot change old sales.

The first spending month uses opening purchasing power. A supplied 1% monthly
inflation path raises the following month's expense to $1,010. The same book
executes identical prior sales when only the last market month changes.
"""

from decimal import Decimal

from tests.market_household_cases import flat
from wealthlab.household.scenario import Scenario
from wealthlab.markets.household_run import run
from wealthlab.markets.inputs import MarketCase
from wealthlab.markets.paths import generate


def spending_case():
    case, market, binding = flat(cash_yield=0)
    data = case.model_dump(mode="json")
    data["expenses"] = [
        dict(
            id="living",
            provenance="illustration",
            start=data["start"],
            end=data["end"],
            monthly_amount="1000",
            currency="USD",
            annual_growth=0,
            category="essential",
        )
    ]
    binding = binding.model_copy(update=dict(inflation_expenses=["living"]))
    return Scenario.model_validate(data), market, binding


def test_realized_inflation_uses_prior_cpi_and_actual_real_wealth():
    case, market, binding = spending_case()
    data = market.model_dump(mode="json")
    data["expected_annual_inflation"] = 1.01**12 - 1
    rows = run(case, generate(MarketCase.model_validate(data)), binding)["details"][0]["rows"]
    assert rows[0]["essential"] == 1000
    assert rows[1]["essential"] == 1010
    assert abs(rows[1]["market_cpi"] - Decimal("1.0201")) < Decimal(".0000001")
    expected = (rows[-1]["net_wealth"] / rows[-1]["market_cpi"]).quantize(Decimal(".01"))
    assert rows[-1]["real_net_wealth"] == expected


def test_future_market_crash_does_not_change_prior_actual_lot_sales():
    case, market, binding = spending_case()
    baseline = run(case, generate(market), binding)["details"][0]["rows"]
    data = market.model_dump(mode="json")
    data.update(
        mode="stress",
        shocks=[dict(name="last month crash", month=23, mark_shocks=dict(equities=-0.5))],
    )
    stressed = run(case, generate(MarketCase.model_validate(data)), binding)["details"][0]["rows"]
    assert [r["closing_cash"] for r in baseline[:23]] == [r["closing_cash"] for r in stressed[:23]]
    assert [r["lot_funding_proceeds"] for r in baseline[:23]] == [
        r["lot_funding_proceeds"] for r in stressed[:23]
    ]
    assert stressed[-1]["net_wealth"] < baseline[-1]["net_wealth"]
