"""One benefit source supplies actual cash, current net tax receipts and carried positions."""

from decimal import Decimal

from wealthlab.retirement.social import run as ordinary
from wealthlab.retirement.social_work import run
from wealthlab.retirement.social_work_case import SocialWorkCase
from wealthlab.retirement.social_work_household_validation import validate
from wealthlab.retirement.social_work_household_wages import realized

ZERO = Decimal(0)


def calculate(scenario):
    if scenario.social_security is None:
        return None
    if scenario.social_work_plan is None:
        return ordinary(scenario.social_security)
    validate(scenario)
    policy = scenario.social_work_plan.model_copy(update=dict(years=realized(scenario)))
    case = SocialWorkCase(claims=scenario.social_security, work=policy)
    result = run(case)
    baseline = result["claims_counterfactual"]
    return {
        **baseline,
        "cash_months": [
            dict(
                member=r["member"],
                payment_month=r["payment_month"],
                issued_before_offsets=r["net_cash"],
            )
            for r in result["monthly_cash"]
        ],
        "work_result": result,
    }


def observe(result, row, start):
    if result is None or "work_result" not in result:
        return
    current = [r for r in result["work_result"]["monthly_cash"] if r["payment_month"] == start]
    fields = (
        "government_receivable",
        "government_overpayment_debt",
        "forecast_withheld",
        "refund_cash",
        "recovered_overpayment",
        "net_cash",
    )
    row.update(
        {f"social_security_{field}": sum((r[field] for r in current), ZERO) for field in fields}
    )
    position = (
        row["social_security_government_receivable"]
        - row["social_security_government_overpayment_debt"]
    )
    row["social_security_government_net_position"] = position
    row["net_wealth"] += position
    if start == result["work_result"]["monthly_cash"][-1]["payment_month"]:
        row["social_security_work_audit"] = result["work_result"]["annual_work_assessments"]
