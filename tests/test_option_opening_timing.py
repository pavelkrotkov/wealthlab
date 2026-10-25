"""Fresh-book preflight/stress observes first-date entitlements and actual same-day settlement."""

import pytest

from wealthlab.products.option_allocation import scale_new_plan
from wealthlab.products.option_engine import run
from wealthlab.products.option_example import synthetic as old_stock
from wealthlab.products.option_household_inputs import OptionPlan
from wealthlab.products.option_purchase_example import unit_plan
from wealthlab.products.option_stress import stress


@pytest.mark.parametrize(
    "side,kind,settlement,strike,capital",
    [("long", "call", "physical", "110", "1000"), ("short", "put", "cash", "1000", "12000")],
)
def test_preflight_rejects_unfunded_same_day_delivery_or_cash_obligation(
    side, kind, settlement, strike, capital
):
    data = unit_plan().model_dump(mode="json")
    case = data["case"]
    case["opening_stock_purchase"] = None
    case["holdings"]["accounts"][0]["cash"] = capital
    case["legs"][0].update(
        side=side, kind=kind, settlement=settlement, strike=strike, style="american"
    )
    case["events"] = [dict(leg_id="stock_call", date="2026-01-01", action="exercise")]
    with pytest.raises(ValueError, match="does not fund native opening"):
        scale_new_plan(OptionPlan.model_validate(data), 1, per_unit_fees_confirmed=True)


def test_buying_on_ex_date_does_not_acquire_old_holders_first_day_dividend():
    data = unit_plan().model_dump(mode="json")
    data["case"]["dividends"] = [dict(ex_date="2026-01-01", pay_date="2026-01-01", per_share="1")]
    case = OptionPlan.model_validate(data).case
    result = run(case)
    assert result["rows"][0]["cash"] == 2497
    assert result["ending"]["cash"] == 13496


def test_stress_first_day_cash_matches_actual_old_holder_dividend_execution():
    case = old_stock("Covered call")
    dividend = case.dividends[0].model_copy(
        update={"ex_date": case.marks[0].date, "pay_date": case.marks[0].date}
    )
    case = case.model_copy(update={"dividends": [dividend]})
    flat = next(row for row in stress(case) if row["stock_shock"] == row["index_shock"] == 0)
    assert flat["wealth"] == run(case)["rows"][0]["wealth"]
