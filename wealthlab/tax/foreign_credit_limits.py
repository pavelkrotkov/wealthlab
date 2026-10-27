"""Ordinary Form1116 source limits and original-vintage use stay separate by basket.

This confirmed profile apportions only the standard deduction. Each basket
has its own source limit; unused capacity cannot subsidize another basket.
Current paid tax uses capacity before original carry vintages. A final native
credit-order pass applies the independently computed total to the federal return.
"""

from decimal import Decimal

from wealthlab.household.calendar import money
from wealthlab.tax.foreign_credit_carries import use_carries

ZERO = Decimal(0)
BASKETS = ("general", "passive")


def calculate(case, baseline, cash_rows):
    fed, year = baseline["federal"], case.annual.policy.year
    current = [row for row in case.income if row.value.date.year == year]
    gross = sum((row.value.dollars() for row in current), ZERO)
    tax_remaining, audit, used = fed["regular_tax_before_credits"], [], {}
    for basket in BASKETS:
        source = source_limit(current, basket, gross, fed)
        cap = min(source["limit"], tax_remaining)
        paid = sum(
            (
                r["credit_tax_usd"]
                for r in cash_rows
                if r["credit_year"] == year and r["basket"] == basket
            ),
            ZERO,
        )
        current_used = min(max(ZERO, paid), cap)
        carry_used = use_carries(case, basket, cap - current_used, used)
        claimed = current_used + carry_used
        tax_remaining -= claimed
        audit.append(
            dict(
                basket=basket,
                **source,
                current_tax=paid,
                current_used=current_used,
                carry_used=carry_used,
                claimed=claimed,
                excess_current=max(ZERO, paid - current_used),
            )
        )
    return audit, used


def source_limit(rows, basket, gross, fed):
    foreign = sum(
        (row.value.dollars() for row in rows if row.country != "US" and row.basket == basket), ZERO
    )
    deduction = money(fed["standard_deduction"] * foreign / gross) if gross else ZERO
    net = max(ZERO, foreign - deduction)
    denominator = fed["taxable_income"]
    ratio = min(Decimal(1), net / denominator) if denominator else ZERO
    return dict(
        gross=foreign,
        allocated_deduction=deduction,
        net=net,
        denominator=denominator,
        limit=money(fed["regular_tax_before_credits"] * ratio),
    )
