"""Negative net equity does not erase leveraged gross positions or unknown issuers."""

from sleeve_market_cases import baseline

from wealthlab.markets.household_run import run
from wealthlab.markets.inputs import MarketCase
from wealthlab.markets.paths import generate


def test_locked_negative_equity_preserves_gross_exposures_and_unknown_issuers():
    household, market, binding = baseline()
    data = market.model_dump(mode="json")
    data.update(
        mode="stress",
        shocks=[
            dict(
                name="lock_squeeze", month=0, mark_shocks=dict(short=4), lock_months=dict(short=12)
            )
        ],
    )
    result = run(household, generate(MarketCase.model_validate(data)), binding)
    row = result["details"][0]["rows"][0]
    assert row["account_balances"]["sleeve"] == 0
    assert row["sleeve_liability"] == 10000
    assert row["market_factor_values"] == dict(long=130000, short=-150000)
    assert row["market_unmeasured_issuer_accounts"] == ["sleeve"]
    assert row["market_max_security_weight"] is None
    assert row["market_unmapped_factor_accounts"] == []
