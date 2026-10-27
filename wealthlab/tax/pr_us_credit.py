"""Current-year ordinary Form 1116 limitation; excluded-income taxes stay disallowed."""

from decimal import Decimal

from wealthlab.tax.pr_credit_limit import limited


def credit(case, result, foreign_rows):
    gross = result["taxable_gross"]
    foreign = sum(row.federal_amount for row in foreign_rows)
    net = max(Decimal(0), gross - result["standard_deduction"])
    foreign_net = net * foreign / gross if gross else Decimal(0)
    paid = case.pr_income_tax_paid_for_us_credit
    validate_credit(case, result, foreign_rows)
    audit = limited(result["income_tax"] - result["niit"], paid, foreign_net, net)
    result["income_tax"] -= audit["allowed"]
    audit["scope"] = (
        "Current-year ordinary/general category; no carry, treaty re-source or NIIT credit"
    )
    return audit


def validate_credit(case, result, foreign_rows):
    paid = case.pr_income_tax_paid_for_us_credit
    if paid and (
        result["amt"] or any(row.kind in {"dividends", "long_term"} for row in case.income)
    ):
        raise ValueError("US credit with preferential income or AMT is unsupported.")
    if paid and any(row.kind not in {"wages", "ordinary"} for row in foreign_rows):
        raise ValueError(
            "US foreign credit currently supports ordinary/general-category income only."
        )
