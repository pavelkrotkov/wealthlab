"""Two independent factors replace prices without rewriting supplied contract economics."""

from drilling_market_cases import edited, price_case

from wealthlab.markets.household_compile import compile_marks
from wealthlab.markets.household_validation import validate
from wealthlab.markets.paths import generate


def test_compiled_prices_use_independent_starting_prices_and_actual_observed_returns():
    case = price_case()
    batch = generate(case.market)
    validate(case.household, batch, case.binding, 0)
    projected = compile_marks(case.household, batch, case.binding, 0)
    rows = projected.drilling_plan.observations
    assert [(r.commodity_price, r.reference_price) for r in rows] == [(110, 100), (99, 120)]
    excluded = {"commodity_price", "reference_price", "reference_locked"}
    assert [r.model_dump(exclude=excluded) for r in rows] == [
        r.model_dump(exclude=excluded) for r in case.household.drilling_plan.observations
    ]
    assert projected.drilling_plan.model_dump(exclude={"observations"}) == (
        case.household.drilling_plan.model_dump(exclude={"observations"})
    )
    assert case.household.drilling_plan.observations[-1].commodity_price == 100


def test_later_price_shock_cannot_rewrite_the_first_observed_commodity_or_share_price():
    first = price_case()
    changed = edited(lambda data: data["market"]["shocks"][1]["mark_shocks"].update(commodity=2))
    original = compile_marks(first.household, generate(first.market), first.binding, 0)
    later = compile_marks(changed.household, generate(changed.market), changed.binding, 0)
    assert original.drilling_plan.observations[0] == later.drilling_plan.observations[0]
    assert original.drilling_plan.observations[-1] != later.drilling_plan.observations[-1]
