"""A market lock retains marked employer value and blocks even confirmed tax-cash rights."""

from employer_market_cases import change, flat

from wealthlab.markets.household_run import run
from wealthlab.markets.inputs import MarketCase
from wealthlab.markets.paths import generate


def test_locked_distribution_remains_requested_unpaid_and_unspendable():
    household, market, binding = flat()
    data = household.model_dump(mode="json")
    data["compensation_plan"]["events"].append(
        dict(
            id="request",
            provenance="assumption",
            date="2026-03-01",
            sequence=0,
            tranche="award",
            kind="distribution",
            amount="10000",
            bucket="vested",
            purpose="tax_distribution",
            election="cash",
        )
    )
    data["compensation_plan"]["tranches"][0]["vested_tax_cash_before_liquidity_confirmed"] = True
    terms = market.model_dump(mode="json")
    terms.update(mode="stress", shocks=[dict(name="lock", month=0, lock_months=dict(employer=12))])
    result = run(change(household, **data), generate(MarketCase.model_validate(terms)), binding)
    rows = result["details"][0]["rows"]
    assert rows[2]["employer_distribution_requested"] == 10000
    assert rows[2]["employer_distribution_cash"] == 0
    assert rows[-1]["employer_locked_vested"] == rows[-1]["employer_vested"]
    request = next(e for e in rows[-1]["employer_event_log"] if e["event"] == "request")
    assert request["blocked_by_liquidity"]
