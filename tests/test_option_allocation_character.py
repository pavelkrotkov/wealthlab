"""New option contracts use actual holding dates, never a carried legacy character label."""

from datetime import date

import pytest

from wealthlab.products.option_allocation import scale_new_plan
from wealthlab.products.option_engine import run
from wealthlab.products.option_household_inputs import OptionPlan
from wealthlab.products.option_purchase_example import unit_plan


def long_cash_contract(end, realized):
    data = unit_plan().model_dump(mode="json")
    case = data["case"]
    case["opening_stock_purchase"] = None
    case["holdings"]["end"] = end
    case["legs"][0].update(
        side="long", settlement="cash", expiry="2028-01-01", federal_character="long_term"
    )
    case["events"] = [dict(leg_id="stock_call", date=realized, action="close", close_price="12")]
    dates = sorted({"2026-01-01", realized, end})
    case["marks"] = [dict(case["marks"][0], date=day, stock="120") for day in dates]
    return OptionPlan.model_validate(data)


@pytest.mark.parametrize(
    "end,expected",
    [("2027-01-01", "short_term"), ("2027-01-02", "long_term")],
)
def test_more_than_one_calendar_year_boundary_uses_actual_contract_disposition(end, expected):
    source = long_cash_contract(end, end)
    plan = scale_new_plan(source, 1, per_unit_fees_confirmed=True)
    result = run(plan.case)
    federal = next(row for row in result["tax"] if row["jurisdiction"] == "federal")
    # $1,200 close receipt -$500 initial premium -$1 opening -$1 closing.
    assert federal["recognized"] == federal[expected] == 698
    assert result["ending"]["cash"] == 12698
    assert plan.case.legs[0].federal_character == expected
    assert source.case.legs[0].federal_character == "long_term"


def test_early_supplied_close_uses_its_date_instead_of_the_later_horizon():
    source = long_cash_contract("2027-01-02", "2026-02-28")
    plan = scale_new_plan(source, 1, per_unit_fees_confirmed=True)
    federal = next(row for row in run(plan.case)["tax"] if row["jurisdiction"] == "federal")
    assert federal["short_term"] == 698
    assert federal["long_term"] == 0
    assert plan.case.legs[0].opened == date(2026, 1, 1)
