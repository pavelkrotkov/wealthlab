"""Forecast withholding is causal; realized wages determine legal charges only after year close.

Current forecasts may use prior-year observed grace history, never a later
realized wage from the same year. Actual excess beyond payable benefits does
not become a separate debt: only benefits actually overpaid can be recovered.
"""

from datetime import date
from decimal import Decimal

from wealthlab.retirement.social_work_assess_year import assess
from wealthlab.retirement.social_work_rules import actual_wages

ZERO = Decimal(0)


def assess_all(case, baseline):
    validate_own_records(baseline["monthly_entitlements"])
    people = {p.id: p for p in case.claims.members}
    used = dict(case.work.grace_used_before_projection)
    months, annual = [], []
    for report in sorted(case.work.years, key=lambda r: (r.year, r.member)):
        rows = [
            r
            for r in baseline["monthly_entitlements"]
            if r["member"] == report.member and r["entitlement_month"].year == report.year
        ]
        forecast = assess(
            people[report.member],
            report.year,
            report.forecast_monthly_wages,
            rows,
            used[report.member],
            True,
        )
        actual = assess(
            people[report.member],
            report.year,
            actual_wages(report),
            rows,
            used[report.member],
            False,
        )
        used[report.member] = actual["grace_used"]
        entries = month_entries(report, rows, forecast, actual, case.work)
        months.extend(entries)
        annual.append(year_summary(report, entries, forecast, actual))
    return months, annual


def validate_own_records(rows):
    if any(r["spousal_excess"] or r["survivor_excess"] for r in rows):
        raise ValueError(
            "Auxiliary/survivor work effects require a separate supported record profile."
        )


def month_entries(report, rows, forecast, actual, policy):
    entries = []
    for row, predicted, assessed in zip(rows, forecast["months"], actual["months"], strict=True):
        entries.append(
            dict(
                member=report.member,
                entitlement_month=row["entitlement_month"],
                payment_month=row["payment_month"],
                baseline_gross=row["issued_before_offsets"],
                forecast_withheld=predicted["cash_held"],
                actual_deduction=assessed["deduction"],
                crediting_month=bool(assessed["deduction"]),
                closed_year_adjustment=predicted["cash_held"] - assessed["deduction"],
                known_date=date(report.year + 1, 1, 1),
                conditional_payment_date=date(report.year + 1, policy.closed_year_payment_month, 1),
            )
        )
    return entries


def year_summary(report, entries, forecast, actual):
    return dict(
        year=report.year,
        member=report.member,
        forecast_annual_excess=forecast["annual_excess"],
        actual_annual_excess=actual["annual_excess"],
        forecast_grace_year=forecast["grace_year"],
        actual_grace_year=actual["grace_year"],
        actual_charged=sum((r["actual_deduction"] for r in entries), ZERO),
        forecast_cash_withheld=sum((r["forecast_withheld"] for r in entries), ZERO),
        crediting_months=sum(r["crediting_month"] for r in entries),
        uncharged_actual_excess=actual["uncharged_excess"],
    )
