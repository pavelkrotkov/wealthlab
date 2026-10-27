"""Original public Tax-Calculator construction independently checks prepared policy reuse."""

from taxcalc import Calculator, Policy

from wealthlab.household.calendar import money
from wealthlab.tax import federal
from wealthlab.tax.facts import Deductions
from wealthlab.tax.federal_engine import records
from wealthlab.tax.mapping import record
from wealthlab.tax.pr_inputs import income


def reference(case, rows, credits):
    year, scale, label = case.baseline.policy.valuation()
    ratio = sum(r.federal_amount for r in rows) / sum(r.federal_amount for r in case.income)
    policy = Policy()
    policy.set_year(year)
    policy.implement_reform(
        {
            "STD": {year: (policy.STD[0] * float(ratio)).tolist()},
            "AlimonyReceived_frac_in_AGI": {year: 1.0},
        },
        print_warnings=False,
    )
    facts = income(rows)
    calc = Calculator(
        policy=policy,
        records=records(record(case.baseline.filing, facts, Deductions(), scale, credits), year),
    )
    calc.advance_to_year(year)
    calc.calc_all()
    raw = {name: money(float(calc.array(name)[0]) * scale) for name in federal.OUTPUTS}
    return federal.breakdown(raw, facts, label)
