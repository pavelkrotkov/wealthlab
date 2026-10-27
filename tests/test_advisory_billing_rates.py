"""Actual eligible AUM selects a sourced whole-base band, including its declared upper bound.

These independently synthetic rates make the economic distinction observable:
$23,000 at 1.2% on the first $10,000 and .4% above yields $43 per fixed quarter;
a whole-base .4% rate yields $23. Neither method is inferred from a provider table.
"""

from decimal import Decimal

import pytest

from tests.advisory_billing_cases import MARGINAL, WHOLE, crossing, quarter
from wealthlab.household.projection import project
from wealthlab.markets.household_run import run


@pytest.mark.parametrize("method,expected", [(MARGINAL, "43"), (WHOLE, "23")])
def test_identical_observed_aum_has_distinct_explicit_rate_method_cash_cost(method, expected):
    scenario = quarter(method)
    original = scenario.model_dump_json()
    final = project(scenario)[-1]
    bill = final["advisory_fee_assessments"][0]
    assert bill["valuation_base"] == 23000
    assert bill["rate_application"] == method
    assert bill["assessed"] == final["advisory_fees_paid"] == Decimal(expected)
    assert final["net_wealth"] == 24000 - Decimal(expected)
    assert scenario.model_dump_json() == original


@pytest.mark.parametrize("base,rate,charge", [("10000", ".012", "30"), ("10000.01", ".004", "10")])
def test_whole_relationship_upper_limit_is_inclusive_with_actual_unscaled_base(base, rate, charge):
    bill = project(quarter(base=base))[-1]["advisory_fee_assessments"][0]
    assert bill["marginal_tiers"] == []
    assert bill["whole_relationship_tier"]["base"] == Decimal(base)
    assert bill["whole_relationship_tier"]["rate"] == Decimal(rate)
    assert bill["whole_relationship_tier"]["upper_limit_inclusive"] is True
    assert bill["assessed"] == Decimal(charge)


def test_actual_dated_price_crossing_changes_rate_on_all_eligible_aum_without_changing_shares():
    scenario, batch, binding = crossing()
    rows = run(scenario, batch, binding)["details"][0]["rows"]
    bills = [row["advisory_fee_assessments"][0] for row in rows[:2]]
    assert [b["valuation_base"] for b in bills] == [100000, 120000]
    assert [b["whole_relationship_tier"]["rate"] for b in bills] == [
        Decimal(".012"),
        Decimal(".004"),
    ]
    assert [b["assessed"] for b in bills] == [Decimal("101.92"), Decimal("36.82")]
    assert rows[-1]["closing_cash"] == Decimal("4861.26")
    assert rows[-1]["net_wealth"] == Decimal("124861.26")
    assert rows[-1]["lot_audit"]["disposals"] == []
