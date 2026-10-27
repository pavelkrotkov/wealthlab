"""A common realized price path drives every exchange security without resampling.

A12% annual price-only return yields112per share after one year. Supplied
allocations stay independent; positive factor cash yield must not be silently
lost or passed into a second receipt. Incomplete factor mappings fail early.
"""

from decimal import Decimal

import pytest
from optimization_cases import changed
from optimization_product_cases import case

from wealthlab.markets.household_compile import compile_marks
from wealthlab.markets.household_validation import validate
from wealthlab.markets.paths import generate
from wealthlab.optimization.compile import compile_candidate


def test_exchange_reuses_same_realized_prices_and_preserves_tax_allocations():
    profile = changed(
        case(), lambda d: d["training"]["assets"][1].update(expected_annual_mark_return=0.12)
    )
    batch = generate(profile.training)
    before = profile.household.model_dump_json()
    bound = compile_marks(profile.household, batch, profile.binding, 0)
    plan = bound.exchange_fund_plan
    assert abs(plan.observations[11].prices["diversified_a"] - 112) < Decimal(".000001")
    assert plan.observations[11].prices["original"] == plan.observations[11].prices["diversified_a"]
    assert (
        plan.observations[0].allocation
        == profile.household.exchange_fund_plan.observations[0].allocation
    )
    assert before == profile.household.model_dump_json()


@pytest.mark.parametrize(
    "field,value,match",
    [
        ("exchange_factors", {}, "explicit exchange"),
        ("sleeves", ["margin_sleeve"], "every household sleeve"),
    ],
)
def test_optimizer_requires_every_product_market_binding(field, value, match):
    profile = changed(case(), lambda d: d["binding"].update({field: value}))
    with pytest.raises(ValueError, match=match):
        compile_candidate(profile, [profile.dimensions[0].choices[0]])


@pytest.mark.parametrize(
    "change,match",
    [
        (lambda d: d["binding"]["exchange_factors"].pop("original"), "every known exchange"),
        (lambda d: d["binding"]["exchange_factors"].update(original="unknown"), "Unknown market"),
        (
            lambda d: d["binding"].update(replace_exchange_observations_confirmed=False),
            "Confirm replacement",
        ),
    ],
)
def test_incomplete_unknown_or_unconfirmed_exchange_factors_are_rejected(change, match):
    profile = changed(case(), change)
    with pytest.raises(ValueError, match=match):
        validate(profile.household, generate(profile.training), profile.binding, 0)


def test_exchange_market_cash_yield_is_not_silently_dropped_or_counted_twice():
    profile = changed(case(), lambda d: d["training"]["assets"][1].update(annual_cash_yield=0.01))
    with pytest.raises(ValueError, match="zero cash yields"):
        compile_marks(profile.household, generate(profile.training), profile.binding, 0)
