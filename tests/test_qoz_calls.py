"""Actual call funding caps eligibility and leaves unsupported source profiles explicit."""

from decimal import Decimal

import pytest
from qoz_cases import flat

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario

D = Decimal


@pytest.mark.parametrize("when,eligible", [("2027-07-31", 80000), ("2027-08-31", 0)])
def test_direct_stock_clock_includes_sale_date_as_day_one(when, eligible):
    data = flat().model_dump(mode="json")
    # February 2 plus 179 days is July 31: the 180th day, rather than August 1.
    data["lot_plan"]["case"]["trades"][0]["date"] = "2027-02-02"
    data["qoz_plan"]["calls"][0]["date"] = when
    rows = project(Scenario.model_validate(data))
    audit = rows[-1]["qoz_audit"]["calls"][0]
    assert audit["deadline"] == "2027-07-31"
    assert audit["funded"] == D(80000)
    assert audit["elected"]["federal"] == D(eligible)


def test_multiple_actual_calls_cannot_defer_the_same_source_gain_twice_or_borrow_cash():
    data = flat().model_dump(mode="json")
    call = data["qoz_plan"]["calls"][0]
    call["amount"] = "60000"
    data["qoz_plan"]["calls"].append(
        dict(call, id="second_call", date="2027-02-28", amount="50000")
    )
    rows = project(Scenario.model_validate(data))
    assert rows[1]["qoz_call_paid"] == D(45000)
    assert rows[1]["qoz_call_unfunded"] == D(5000)
    assert rows[1]["closing_cash"] == 0
    audits = rows[-1]["qoz_audit"]["calls"]
    assert sum(a["elected"]["federal"] for a in audits) == D(80000)
    assert sum(a["elected"]["new_jersey"] for a in audits) == D(70000)
    assert sum(a["funded"] for a in audits) == D(105000)
    assert rows[1]["qoz_nav"] == D(105000)


@pytest.mark.parametrize(
    "change,message",
    [
        ("future_source", "already executed"),
        ("unknown_source", "already executed"),
        ("unconfirmed_nj", "Confirm independent"),
        ("nonzero_opening", "opens at zero"),
        ("cross_year", "Cross-year QOZ"),
        ("overlap", "share ownership"),
    ],
)
def test_unsupported_profiles_fail_before_a_plausible_result(change, message):
    data = flat().model_dump(mode="json")
    if change == "future_source":
        data["lot_plan"]["case"]["trades"][0]["date"] = "2027-02-15"
    elif change == "unknown_source":
        data["qoz_plan"]["calls"][0]["source_trade_id"] = "missing"
    elif change == "unconfirmed_nj":
        data["qoz_plan"]["new_jersey"] = "unconfirmed"
    elif change == "nonzero_opening":
        data["accounts"][2]["balance"] = "1"
    elif change == "overlap":
        data["qoz_plan"]["account_id"] = "brokerage"
        data["accounts"][1]["balance"] = "0"
        # Product ownership is validated independently before the linked opening valuation.
        from wealthlab.products.qoz_validation import validate_account

        scenario = Scenario.model_validate(data)
        with pytest.raises(ValueError, match=message):
            validate_account(scenario, scenario.qoz_plan)
        return
    else:
        data = flat(2026, 2).model_dump(mode="json")
        data["qoz_plan"]["calls"][0]["date"] = "2027-01-31"
        data["lot_plan"]["case"]["trades"][0]["date"] = "2026-12-15"
    with pytest.raises(ValueError, match=message):
        project(Scenario.model_validate(data))
