"""Observed market locks keep intended saving in cash; future shocks cannot alter past buys."""

from wealthlab.products.life_comparison import compare
from wealthlab.products.life_comparison_inputs import LifeComparison
from wealthlab.products.life_comparison_markets import synthetic


def stressed(shock):
    data = synthetic("deterministic").model_dump(mode="json")
    data["market"].update(mode="stress", shocks=[shock])
    return LifeComparison.model_validate(data)


def test_locked_markets_leave_optional_saving_in_spendable_cash():
    result = compare(
        stressed(dict(name="No purchase liquidity", month=0, lock_months={"equities": 3}))
    )
    reference = result["alternatives"]["liquid_term"]["outcomes"][0]
    assert reference["saving_spent"] == 0
    assert reference["saving_unfilled"] == 1800
    assert reference["closing_cash"] == 6700
    assert reference["funding_failure_months"] == 0


def first_purchase(result):
    row = result["alternatives"]["liquid_term"]["details"][0]["rows"][-1]
    return row["saving_audit"][0]["trades"]


def test_a_later_crash_does_not_change_the_earlier_observed_purchase():
    ordinary = compare(synthetic("deterministic"))
    crash = compare(stressed(dict(name="Later crash", month=2, mark_shocks={"equities": -0.9})))
    assert first_purchase(ordinary) == first_purchase(crash)
    assert (
        ordinary["alternatives"]["liquid_term"]["outcomes"][0]["marked_wealth_after_recognized_tax"]
        > crash["alternatives"]["liquid_term"]["outcomes"][0]["marked_wealth_after_recognized_tax"]
    )
