"""Conditional interpretations require supplied source confirmation, never a silent guess.

An annual fraction does not authorize future observations, earlier payment or
advance refund/proration rights. Legacy absent fields retain native defaults.
"""

from decimal import Decimal

import pytest

from tests.advisory_billing_cases import quarter
from tests.advisory_cases import change
from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario


def test_whole_base_rate_needs_explicit_sourced_breakpoint_interpretation():
    scenario = change(
        quarter(),
        lambda p: p["schedules"][0].update(whole_relationship_breakpoints_source_confirmed=False),
    )
    with pytest.raises(ValueError, match="sourced inclusive breakpoint"):
        project(scenario)


@pytest.mark.parametrize("fraction,confirmed", [(".25", False), (None, True)])
def test_fixed_fraction_and_its_source_confirmation_must_be_supplied_together(fraction, confirmed):
    scenario = change(
        quarter(),
        lambda p: p["schedules"][0]["periods"][0].update(
            fixed_annual_period_fraction=fraction, fixed_fraction_source_confirmed=confirmed
        ),
    )
    with pytest.raises(ValueError, match="source confirmation together"):
        project(scenario)


@pytest.mark.parametrize("fraction", ["0", "-.25", "1.25", "NaN"])
def test_invalid_or_nonfinite_annual_fraction_is_rejected_before_cash_execution(fraction):
    with pytest.raises(ValueError):
        quarter(fraction=fraction)


def test_missing_new_fields_retains_legacy_marginal_actual_days_arithmetic():
    data = quarter().model_dump(mode="json")
    schedule = data["advisory_fee_plan"]["schedules"][0]
    schedule.pop("rate_application")
    schedule.pop("whole_relationship_breakpoints_source_confirmed")
    period = schedule["periods"][0]
    period.pop("fixed_annual_period_fraction")
    period.pop("fixed_fraction_source_confirmed")
    bill = project(Scenario.model_validate(data))[-1]["advisory_fee_assessments"][0]
    assert bill["rate_application"] == "progressive_marginal"
    assert bill["whole_relationship_tier"] is None
    assert bill["assessed"] == (Decimal(172) * 90 / 365).quantize(Decimal(".01"))


def test_fixed_fraction_does_not_bypass_independent_advance_refund_terms():
    scenario = change(
        quarter(),
        lambda p: p["schedules"][0]["periods"][0].update(
            valuation_date="2026-01-31", assessment_date="2026-01-31", payment_due_date="2026-01-31"
        ),
    )
    with pytest.raises(ValueError, match="nonrefundable/no-proration"):
        project(scenario)


def test_actual_day_period_cannot_replace_an_unknown_day_count_with_a_default():
    scenario = change(quarter(fraction=None), lambda p: p["schedules"][0].pop("day_count"))
    with pytest.raises(ValueError, match="supplied annual day count"):
        project(scenario)
