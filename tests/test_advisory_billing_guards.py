"""Conditional interpretations require supplied source confirmation, never a silent guess.

An annual fraction does not authorize future observations, earlier payment or
advance refund/proration rights. Legacy absent fields retain native defaults.
"""

import pytest

from tests.advisory_billing_cases import quarter
from tests.advisory_cases import change
from wealthlab.household.projection import project


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
