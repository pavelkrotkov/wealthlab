"""Every QOZ allocation pays the same sourced outer fees from actual observed whole capital."""

from calendar import monthrange
from decimal import ROUND_HALF_UP, Decimal

from optimization_qoz_cases import case

from wealthlab.optimization.advisory_example import extend
from wealthlab.optimization.search import search


def independent_cash():
    balance = Decimal(105000)
    for month in range(1, 13):
        annual = min(balance, Decimal(100000)) * Decimal(".01") + max(
            Decimal(0), balance - 100000
        ) * Decimal(".005")
        fee = (annual * monthrange(2027, month)[1] / 365).quantize(
            Decimal(".01"), rounding=ROUND_HALF_UP
        )
        balance -= fee
    return balance - 1247


def test_native_qoz_and_outer_fees_conserve_every_subscription_and_heldout_cash():
    profile = extend(case())
    result = search(profile)
    expected = independent_cash()
    assert [c["median_real_after_tax_exit_wealth"] for c in result["candidates"]] == [expected] * 4
    assert result["held_out"]["assessment"]["median_real_after_tax_exit_wealth"] == expected
    rows = result["selected_training"]["details"][0]["rows"]
    assert sum(r["advisory_fees_paid"] for r in rows) == 105000 - 1247 - expected
    assert rows[-1]["advisory_fees_owed"] == 0
    assert result["configured_validation_passed"]
