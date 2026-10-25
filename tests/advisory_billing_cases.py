"""Independent synthetic rate/period contracts supply every optional interpretation explicitly."""

from datetime import date, timedelta

from tests.advisory_cases import native, plain, with_fee
from wealthlab.household.advisory_example import plan
from wealthlab.household.calendar import months
from wealthlab.household.scenario import Scenario

WHOLE = "whole_relationship_breakpoint"
MARGINAL = "progressive_marginal"


def quarter(method=WHOLE, base="23000", cash="1000", year=2026, number=1, fraction=".25"):
    start = date(year, number * 3 - 2, 1)
    end = date(year + number // 4, number % 4 * 3 + 1, 1)
    original = plain(cash=cash, asset=base).model_dump(mode="json")
    original.update(start=f"{year}-01-01", end=end.isoformat())
    scenario = Scenario.model_validate(original)
    data = plan(scenario).model_dump(mode="json")
    schedule = data["schedules"][0]
    schedule.update(
        source_ref="Original synthetic inclusive-breakpoint or marginal contract; no actual quote",
        covered=[dict(account_id="brokerage", value_basis="modeled_net_account_equity")],
        tiers=[
            dict(upper_limit="10000", annual_rate=".012"),
            dict(upper_limit=None, annual_rate=".004"),
        ],
        rate_application=method,
        whole_relationship_breakpoints_source_confirmed=method == WHOLE,
        periods=[
            dict(
                accrual_start=start.isoformat(),
                accrual_end=end.isoformat(),
                valuation_date=(end - timedelta(days=1)).isoformat(),
                assessment_date=(end - timedelta(days=1)).isoformat(),
                payment_due_date=(end - timedelta(days=1)).isoformat(),
                fixed_annual_period_fraction=fraction,
                fixed_fraction_source_confirmed=fraction is not None,
            )
        ],
    )
    original["advisory_fee_plan"] = data
    return Scenario.model_validate(original)


def crossing():
    scenario, batch, binding = native(
        shocks=[dict(name="original_growth", month=1, mark_shocks=dict(source_stock=".2"))]
    )
    data = with_fee(scenario).model_dump(mode="json")
    schedule = data["advisory_fee_plan"]["schedules"][0]
    schedule.update(
        source_ref="Original synthetic whole-base rate across actual shared-path marks",
        day_count=365,
        rate_application=WHOLE,
        whole_relationship_breakpoints_source_confirmed=True,
        tiers=[
            dict(upper_limit="110000", annual_rate=".012"),
            dict(upper_limit=None, annual_rate=".004"),
        ],
        periods=[
            dict(
                accrual_start=str(start),
                accrual_end=str(end),
                valuation_date=str(end - timedelta(days=1)),
                assessment_date=str(end - timedelta(days=1)),
                payment_due_date=str(end - timedelta(days=1)),
            )
            for start, end in months(date(2026, 1, 1), date(2026, 3, 1))
        ],
    )
    return Scenario.model_validate(data), batch, binding
