"""Independent household cash and wealth identities for actual policy funding."""

from wealthlab.household.projection import project
from wealthlab.products.life_household_example import synthetic


def test_funded_premiums_and_loan_preserve_one_net_policy_asset():
    rows = project(synthetic())
    final = rows[-1]
    assert [r["closing_cash"] for r in rows] == [48000, 46000, 45500]
    assert final["account_balances"]["life_policy"] == 11500
    assert final["net_wealth"] == 57000
    assert final["life_policy_values"][0]["loan"] == 500
    assert final["life_net_death_benefit"] == 99500
    assert final["life_protection_shortfall"] == 50500


def test_dated_reserve_does_not_annualize_a_lump_premium_and_shows_retirement():
    rows = project(synthetic())
    assert [r["life_reserve_target"] for r in rows] == [3000, 2000, 2000]
    assert [r["reserve_target"] for r in rows] == [27000, 26000, 26000]
    assert [r["life_retirement_premiums_paid"] for r in rows] == [0, 1000, 0]
    assert rows[-1]["life_future_retirement_premiums"] == 2000
