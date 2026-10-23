"""Apply real cash payments once and separate refunds across jurisdictions."""

from decimal import Decimal

from wealthlab.household.calendar import money
from wealthlab.tax.annual import AnnualCase


def pay(case: AnnualCase, wallet, requested: dict[str, Decimal]) -> tuple[AnnualCase, Decimal]:
    values = case.payments.model_dump()
    total = Decimal(0)
    for field, due in requested.items():
        paid = wallet.pay(max(Decimal(0), money(due)))
        values[field] += paid
        total += paid
    updated = type(case.payments).model_validate(values)
    return case.model_copy(update={"payments": updated}), total


def balances(result: dict) -> dict[str, Decimal]:
    # Federal payroll reconciliation can affect the same federal settlement.
    # An NJ refund, however, cannot pay a federal bill before it arrives.
    return dict(
        federal=result["federal_income_balance"] + result["payroll_balance"],
        new_jersey=result["nj_balance"],
    )


def settle(case: AnnualCase, wallet, result: dict) -> tuple[AnnualCase, Decimal]:
    federal = max(Decimal(0), balances(result)["federal"])
    payroll = min(federal, max(Decimal(0), result["payroll_balance"]))
    requested = dict(
        employee_payroll_withheld=payroll,
        federal_estimates=federal - payroll,
        nj_estimates=max(Decimal(0), result["nj_balance"]),
    )
    return pay(case, wallet, requested)


def withholding_request(amounts: dict, plan, result: dict, start, end) -> dict:
    wages = sum(
        (
            amounts[rule.income_id]
            for rule in plan.income_rules
            if rule.federal in {"wages_primary", "wages_spouse"}
        ),
        Decimal(0),
    )
    state_wages = sum(
        (amounts[rule.income_id] for rule in plan.income_rules if rule.new_jersey == "wages"),
        Decimal(0),
    )
    requested = dict(
        employee_payroll_withheld=max(Decimal(0), result["payroll_balance"]),
        federal_income_withheld=wages * plan.federal_wage_withholding,
        nj_withheld=state_wages * plan.nj_wage_withholding,
    )
    requested.update(estimated_requests(plan, start, end))
    return requested


def estimated_requests(plan, start, end) -> dict:
    events = [item for item in plan.estimated_payments if start <= item.date < end]
    return dict(
        federal_estimates=sum((item.federal for item in events), Decimal(0)),
        nj_estimates=sum((item.new_jersey for item in events), Decimal(0)),
    )
