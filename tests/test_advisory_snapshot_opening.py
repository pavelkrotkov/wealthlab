"""Advance bills use a real opening snapshot and preserve the entire separate accrual span."""

from datetime import date
from decimal import Decimal

from tests.advisory_cases import change, plain, with_fee
from wealthlab.household.projection import project


def test_full_advance_quarter_uses_actual_opening_value_without_backdating_cash():
    case = with_fee(plain().model_copy(update=dict(end=date(2026, 5, 1))))

    def advance(plan):
        plan["valuation_timing"] = "explicit_observed_snapshot_cutoffs"
        schedule = plan["schedules"][0]
        schedule["advance_nonrefundable_no_proration_assumed_confirmed"] = True
        schedule["periods"][0].update(
            accrual_start="2026-02-01",
            accrual_end="2026-05-01",
            valuation_date="2026-01-01",
            valuation_cutoff="opening",
        )

    rows = project(change(case, advance))
    bill = rows[0]["advisory_fee_assessments"][0]
    # Feb28 +Mar31 +Apr30 =89 actual accrual days, charged January31 using January1 AUM.
    assert bill["period_days"] == 89
    assert bill["valuation_base"] == 100000
    assert bill["assessed"] == rows[0]["advisory_fees_paid"] == Decimal("247.22")
    assert rows[-1]["net_wealth"] == Decimal("104752.78")
    audit = rows[-1]["advisory_fee_audit"]
    assert audit["observed_snapshots"][0]["date"] == "2026-01-01"
    assert audit["payments"][0]["date"] == "2026-01-31"
