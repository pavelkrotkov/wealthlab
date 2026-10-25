"""Actual accrual spans stay separate from observation, assessment and payment-due dates."""

from decimal import Decimal

import pytest

from tests.advisory_cases import change, native, with_fee
from wealthlab.household.projection import project


def test_full_quarter_arrears_uses_all_ninety_days_without_shortening_to_last_month():
    case, _, _ = native()
    case = with_fee(case)

    def quarter(plan):
        plan["schedules"][0]["periods"][0].update(
            accrual_end="2026-04-01",
            valuation_date="2026-03-31",
            assessment_date="2026-03-31",
            payment_due_date="2026-03-31",
        )

    rows = project(change(case, quarter))
    assert rows[0]["advisory_fees_assessed"] == rows[1]["advisory_fees_assessed"] == 0
    assert rows[2]["advisory_fees_assessed"] == Decimal(250)
    assert rows[2]["advisory_fee_assessments"][0]["period_days"] == 90


@pytest.mark.parametrize(
    "updates, message",
    [
        (dict(accrual_start="2025-12-01"), "source and availability"),
        (dict(accrual_end="2026-04-01"), "Advance advisory billing"),
        (dict(assessment_date="2026-01-15"), "month-end date"),
        (dict(valuation_date="2026-01-01"), "same-date observed valuation"),
        (dict(payment_due_date="2026-02-28"), "billing and due date"),
    ],
)
def test_unknown_accrual_or_unavailable_snapshot_dates_fail_explicitly(updates, message):
    case, _, _ = native()
    case = with_fee(case)
    with pytest.raises(ValueError, match=message):
        project(change(case, lambda p: p["schedules"][0]["periods"][0].update(updates)))
