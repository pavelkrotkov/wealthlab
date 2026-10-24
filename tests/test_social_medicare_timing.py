"""The current coverage month's premium is deducted from the prior entitlement's check.

The two calendars stay distinct at July enrollment. Part D retains its cents
after the monthly benefit has already passed the Part B rounding stage.
"""

from datetime import date
from decimal import Decimal

from wealthlab.household.projection import project
from wealthlab.retirement.social_medicare_example import synthetic


def test_july_coverage_changes_july_payment_for_june_entitlement():
    case = synthetic()
    source = case.medicare_plan.case
    coverage = [
        c.model_copy(update=dict(start=date(2030, 7, 1))) if c.member == "person" else c
        for c in source.coverage
    ]
    plan = case.medicare_plan.model_copy(
        update=dict(case=source.model_copy(update=dict(coverage=coverage)))
    )
    rows = project(case.model_copy(update=dict(medicare_plan=plan)))
    assert rows[5]["social_security_cash"] == 4147
    assert rows[6]["social_security_cash"] == 3944
    july = payment_for(rows, "person", date(2030, 7, 1))
    assert july["entitlement_month"] == date(2030, 6, 1)
    assert july["part_b_withheld"] == Decimal("202.90")


def test_high_prior_income_collects_part_d_irmaa_after_rounding():
    case = synthetic()
    source = case.medicare_plan.case
    history = [
        source.income_history[0].model_copy(update=dict(agi=Decimal(301000))),
        source.income_history[1],
    ]
    plan = case.medicare_plan.model_copy(
        update=dict(case=source.model_copy(update=dict(income_history=history)))
    )
    rows = project(case.model_copy(update=dict(medicare_plan=plan)))
    assert rows[1]["social_security_cash"] == 3463
    assert rows[1]["social_security_part_d_irmaa_withheld"] == 75
    assert rows[1]["social_security_gross_credited"] == Decimal("4349.60")
    assert rows[1]["medicare_cash_paid"] == 480
    assert payment_for(rows, "person", date(2030, 2, 1))["cash_received"] == Decimal("2656.50")


def payment_for(rows, member, when):
    payments = rows[-1]["medicare_audit"]["benefit_payments"]
    return next(p for p in payments if p["member"] == member and p["payment_month"] == when)
