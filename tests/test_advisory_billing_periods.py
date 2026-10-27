"""Supplied quarter fractions never masquerade as shortened accrual or payment dates.

The same annual $92 whole-base charge has a fixed $23 quarter cost across actual
90/91/92-day spans and explicit annual day counts. A missing fraction preserves
the original actual-days arithmetic, with no implied refund or holiday rule.
"""

from decimal import Decimal

import pytest

from tests.advisory_billing_cases import quarter
from tests.advisory_cases import change
from wealthlab.household.projection import project


@pytest.mark.parametrize(
    "year,number,days", [(2026, 1, 90), (2024, 1, 91), (2026, 2, 91), (2026, 3, 92)]
)
@pytest.mark.parametrize("day_count", [360, 365, 366])
def test_sourced_fixed_quarter_keeps_true_dates_and_ignores_annual_day_count(
    year, number, days, day_count
):
    scenario = change(
        quarter(year=year, number=number), lambda p: p["schedules"][0].update(day_count=day_count)
    )
    rows = project(scenario)
    bill = rows[-1]["advisory_fee_assessments"][0]
    assert bill["assessed"] == 23
    assert bill["period_days"] == days
    assert bill["fixed_annual_period_fraction"] == Decimal(".25")
    assert bill["applied_day_count"] is None
    assert bill["period_factor_basis"] == "supplied_fixed_annual_fraction"
    assert bill["date"] == bill["valuation_date"] == bill["payment_due_date"]
    assert sum(r["advisory_fees_paid"] for r in rows) == 23


@pytest.mark.parametrize("year,days", [(2026, 90), (2024, 91)])
def test_absent_fixed_fraction_retains_exact_default_actual_days_division(year, days):
    bill = project(quarter(year=year, fraction=None))[-1]["advisory_fee_assessments"][0]
    assert bill["assessed"] == (Decimal(92) * days / 365).quantize(Decimal(".01"))
    assert bill["applied_day_count"] == 365
    assert bill["fixed_annual_period_fraction"] is None
    assert bill["period_factor_basis"] == "actual_days_over_day_count"


def test_fixed_quarter_can_omit_an_unknown_unused_annual_day_count():
    scenario = change(quarter(), lambda p: p["schedules"][0].pop("day_count"))
    bill = project(scenario)[-1]["advisory_fee_assessments"][0]
    assert bill["assessed"] == 23
    assert bill["day_count"] is bill["applied_day_count"] is None


def test_confirmed_fixed_quarter_advance_keeps_full_span_and_actual_january_payment():
    def advance(plan):
        schedule = plan["schedules"][0]
        schedule["advance_nonrefundable_no_proration_assumed_confirmed"] = True
        schedule["periods"][0].update(
            valuation_date="2026-01-31", assessment_date="2026-01-31", payment_due_date="2026-01-31"
        )

    rows = project(change(quarter(), advance))
    bill = rows[0]["advisory_fee_assessments"][0]
    assert bill["assessed"] == rows[0]["advisory_fees_paid"] == 23
    assert bill["period_days"] == 90
    assert bill["accrual_end_exclusive"] == "2026-04-01"
    assert bill["date"] == bill["payment_due_date"] == "2026-01-31"
    assert rows[-1]["closing_cash"] == 977
    assert rows[-1]["advisory_fees_assessed"] == rows[-1]["fees_owed"] == 0
