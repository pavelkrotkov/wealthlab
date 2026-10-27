"""Ordinary-election PR tax and independently limited regular/ABT US-tax credits."""

from decimal import Decimal

from wealthlab.household.calendar import money
from wealthlab.tax.pr_credit_allocation import allocation
from wealthlab.tax.pr_credit_limit import limited
from wealthlab.tax.pr_local_rates import abt, regular
from wealthlab.tax.pr_residence import MET


def calculate(case, rows, us_tax):
    gross = sum((row.pr_amount for row in rows), Decimal(0))
    exemption = Decimal(7000 if case.baseline.filing.status == "joint" else 3500)
    if case.pr_allowed_deductions > gross:
        raise ValueError("Allowed PR deductions exceed the supported positive income base.")
    net = max(Decimal(0), gross - case.pr_allowed_deductions - exemption)
    normal = regular(net, exemption, gross)
    abt_net_income = max(Decimal(0), gross - case.pr_abt_allowed_deductions - exemption)
    wage_only = all(row.kind == "wages" for row in rows)
    reported = case.pr_wages_reported_on_form_499r2 in MET
    tentative = abt(abt_net_income, wage_only=wage_only and reported)
    source = source_allocation(rows, gross, case.pr_allowed_deductions + exemption)
    credit = limited(normal["tax"], us_tax, source["source_net"], net)
    abt_source = source_allocation(rows, gross, case.pr_abt_allowed_deductions + exemption)
    abt_credit = limited(tentative, us_tax, abt_source["source_net"], abt_net_income)
    regular_net = normal["tax"] - credit["allowed"]
    abt_net = tentative - abt_credit["allowed"]
    return dict(
        gross=gross,
        allowed_deductions=case.pr_allowed_deductions,
        exemption=exemption,
        net=net,
        regular=normal,
        regular_credit=credit,
        regular_source_allocation=source,
        abt_net_income=abt_net_income,
        abt=tentative,
        abt_credit=abt_credit,
        abt_source_allocation=abt_source,
        additional_abt=max(Decimal(0), abt_net - regular_net),
        income_tax=money(max(regular_net, abt_net)),
        election="Ordinary rates; preferential elections require a separate supported profile",
        next_abt_credit=max(Decimal(0), abt_net - regular_net),
    )


def source_allocation(rows, gross, deductions):
    # This positive ordinary profile has only unassigned deductions; allocate
    # them proportionally. Direct expenses/losses require another profile.
    source_gross = sum((row.pr_amount for row in rows if row.pr_source == "US"), Decimal(0))
    return allocation(gross, source_gross, deductions)
