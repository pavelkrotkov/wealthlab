"""A market sale lock preserves marked wealth while the actual medical bill fails."""

from wealthlab.markets.household_run import paired, run
from wealthlab.markets.hsa_example import synthetic
from wealthlab.markets.paths import generate


def test_illiquid_hsa_income_stays_cash_but_cannot_make_locked_shares_spendable():
    household, market, binding = synthetic("stress", "illiquidity")
    batch = generate(market)
    result = run(household, batch, binding)
    rows = result["details"][0]["rows"]
    audit = rows[-1]["hsa_audit"]["investments"]
    assert not audit["executed_trades"]
    assert rows[-1]["medical_provider_paid"] < 5000
    assert rows[-1]["medical_owed"] > 0
    assert rows[-1]["net_wealth"] > 0
    assert result["aggregate"]["successes"] == 0
    assert paired(result, result)[0]["real_wealth_change"] == 0
