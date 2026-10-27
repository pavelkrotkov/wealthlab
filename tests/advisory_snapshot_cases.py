"""Explicit original billing contracts isolate named observed dates and full accrual spans."""

from tests.advisory_cases import change, with_fee


def snapshot_fee(
    case,
    *,
    account="brokerage",
    cutoff="opening",
    valued="2026-01-01",
    billed="2026-01-31",
    start="2026-01-01",
    end="2026-01-31",
    rate=".01",
    advance=False,
):
    case = with_fee(case, account=account, rate=rate)

    def configure(plan):
        plan["valuation_timing"] = "explicit_observed_snapshot_cutoffs"
        schedule = plan["schedules"][0]
        schedule["advance_nonrefundable_no_proration_assumed_confirmed"] = advance
        schedule["periods"][0].update(
            accrual_start=start,
            accrual_end=end,
            valuation_date=valued,
            valuation_cutoff=cutoff,
            assessment_date=billed,
            payment_due_date=billed,
        )

    return change(case, configure)
