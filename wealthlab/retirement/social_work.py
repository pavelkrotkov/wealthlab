"""Own-record work deductions, closed-year positions and conditional cash settlement."""

from decimal import Decimal

from wealthlab.retirement.social import run as ordinary
from wealthlab.retirement.social_work_arf import adjustments
from wealthlab.retirement.social_work_assessment import assess_all
from wealthlab.retirement.social_work_cash import project

ZERO = Decimal(0)
SOURCES = [
    "https://secure.ssa.gov/poms.nsf/links/0302501025",
    "https://secure.ssa.gov/poms.nsf/links/0302501080",
    "https://secure.ssa.gov/poms.nsf/lnx/0302501030",
    "https://secure.ssa.gov/poms.nsf/lnx/0302501100",
    "https://secure.ssa.gov/poms.nsf/lnx/0302501110",
    "https://secure.ssa.gov/poms.nsf/lnx/0300615480",
    "https://secure.ssa.gov/poms.nsf/lnx/0300615482",
]


def run(case):
    baseline = ordinary(case.claims)
    assessed, annual_work = assess_all(case, baseline)
    arfs = adjustments(case, baseline, assessed)
    cash = project(case, baseline, assessed, arfs)
    return dict(
        monthly_cash=cash,
        annual_cash=annual(cash),
        annual_work_assessments=annual_work,
        monthly_work_assessments=assessed,
        reduction_factor_adjustments=arfs,
        total_net_cash=sum((r["net_cash"] for r in cash), ZERO),
        rule_mode=case.work.rule_mode,
        claims_counterfactual=baseline,
        sources=SOURCES,
    )


def annual(rows):
    totals = {}
    fields = ("net_cash", "refund_cash", "recovered_overpayment", "forecast_withheld")
    for row in rows:
        key = row["payment_month"].year, row["member"]
        target = totals.setdefault(key, dict.fromkeys(fields, ZERO))
        for field in fields:
            target[field] += row[field]
    return [dict(year=year, member=member, **values) for (year, member), values in totals.items()]
