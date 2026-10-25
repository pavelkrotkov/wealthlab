"""Fresh public Tax-Calculator policy with the Pub 570 standard-deduction ratio."""

from decimal import Decimal

from taxcalc import Calculator, Policy

from wealthlab.household.calendar import money
from wealthlab.tax import federal
from wealthlab.tax.facts import Deductions
from wealthlab.tax.federal_engine import records
from wealthlab.tax.mapping import record
from wealthlab.tax.pr_inputs import income
from wealthlab.tax.pr_us_credit import credit


def calculate(case, taxable_rows, foreign_rows):
    policy_year, scale, label = case.baseline.policy.valuation()
    gross = sum(row.federal_amount for row in case.income)
    taxable_gross = sum(row.federal_amount for row in taxable_rows)
    ratio = taxable_gross / gross if gross else Decimal(0)
    policy = Policy()
    policy.set_year(policy_year)
    standard = (policy.STD[0] * float(ratio)).tolist()
    policy.implement_reform(
        {"STD": {policy_year: standard}, "AlimonyReceived_frac_in_AGI": {policy_year: 1.0}},
        print_warnings=False,
    )
    taxable = income(taxable_rows)
    calc = Calculator(
        policy=policy,
        records=records(record(case.baseline.filing, taxable, Deductions(), scale), policy_year),
    )
    calc.advance_to_year(policy_year)
    calc.calc_all()
    values = {name: money(float(calc.array(name)[0]) * scale) for name in federal.OUTPUTS}
    if values["refund"]:
        raise ValueError(
            "Federal refundable-credit residence eligibility needs a supported profile."
        )
    result = federal.breakdown(values, taxable, label)
    result.update(worldwide_gross=gross, taxable_gross=taxable_gross, standard_ratio=ratio)
    result["foreign_credit"] = credit(case, result, foreign_rows)
    return result
