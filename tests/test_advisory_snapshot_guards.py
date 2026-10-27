"""Unknown cutoff data and contractual refund rights cannot be replaced by future marks or cash."""

from datetime import date

import pytest

from tests.advisory_cases import change, plain
from tests.advisory_snapshot_cases import snapshot_fee
from wealthlab.household.projection import project


@pytest.mark.parametrize(
    "cutoff, valued, message",
    [
        ("opening", "2025-12-31", "available past snapshot"),
        ("opening", "2026-02-01", "never a future date"),
        ("opening", "2026-01-15", "snapshot is unavailable"),
        ("completed_month_end", "2026-01-31", "snapshot is unavailable"),
    ],
)
def test_unsupported_or_not_yet_executed_snapshot_has_no_stale_fallback(cutoff, valued, message):
    case = snapshot_fee(plain(), cutoff=cutoff, valued=valued)
    with pytest.raises(ValueError, match=message):
        project(case)


def test_unknown_refund_rights_and_first_day_billing_are_guarded_instead_of_relabeling_dates():
    case = plain().model_copy(update=dict(end=date(2026, 5, 1)))
    with pytest.raises(ValueError, match="sourced nonrefundable"):
        project(snapshot_fee(case, start="2026-02-01", end="2026-05-01"))
    with pytest.raises(ValueError, match="month-end date"):
        project(snapshot_fee(case, billed="2026-01-01"))


def test_advance_terms_must_be_available_at_actual_billing_not_just_at_future_accrual_start():
    case = snapshot_fee(
        plain().model_copy(update=dict(end=date(2026, 5, 1))),
        start="2026-02-01",
        end="2026-05-01",
        advance=True,
    )

    def unavailable(plan):
        plan["schedules"][0].update(source_date="2026-02-01", available_on="2026-02-01")

    with pytest.raises(ValueError, match="source and availability"):
        project(change(case, unavailable))
