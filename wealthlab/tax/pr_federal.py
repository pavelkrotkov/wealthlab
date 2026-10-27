"""Fresh public Tax-Calculator policy with the Pub 570 standard-deduction ratio."""

from decimal import Decimal

from wealthlab.household.calendar import money
from wealthlab.tax import federal
from wealthlab.tax.facts import Deductions
from wealthlab.tax.mapping import record
from wealthlab.tax.pr_federal_engine import values as prepared_values
from wealthlab.tax.pr_inputs import income
from wealthlab.tax.pr_us_credit import credit


def calculate(case, taxable_rows, foreign_rows, *, native_credits=None):
    policy_year, scale, label = case.baseline.policy.valuation()
    gross = sum(row.federal_amount for row in case.income)
    taxable_gross = sum(row.federal_amount for row in taxable_rows)
    ratio = taxable_gross / gross if gross else Decimal(0)
    taxable = income(taxable_rows)
    raw = prepared_values(
        record(case.baseline.filing, taxable, Deductions(), scale, native_credits),
        policy_year,
        ratio,
        federal.OUTPUTS,
    )
    values = {name: money(value * scale) for name, value in raw.items()}
    if values["refund"]:
        raise ValueError(
            "Federal refundable-credit residence eligibility needs a supported profile."
        )
    result = federal.breakdown(values, taxable, label)
    result.update(worldwide_gross=gross, taxable_gross=taxable_gross, standard_ratio=ratio)
    result["foreign_credit"] = (
        credit(case, result, foreign_rows)
        if native_credits is None
        else native_credit_audit(native_credits, result)
    )
    return result


def native_credit_audit(credits, result):
    """Native taxbc is the same prepared return's regular tax before any credit."""
    if credits.eligibility == "allowed" and credits.regular > result["regular_tax_before_credits"]:
        raise ValueError("PR prepared regular credit exceeds its actual pre-credit regular tax.")
    return dict(
        method="One native prepared-policy e07300/e62900 computation; legacy subtraction bypassed",
        supplied_regular=credits.regular,
        supplied_amt=credits.alternative_minimum,
        actual_regular=result["foreign_tax_credit"],
        eligibility=credits.eligibility,
        source=credits.source,
    )
