"""Single-filer federal controls isolate ordinary tax from earned/investment classifications."""

from wealthlab.tax.facts import Deductions, FederalIncome
from wealthlab.tax.federal import calculate
from wealthlab.tax.filing import Filing
from wealthlab.tax.policy import TaxPolicy


def compute(income, policy=None, age=40):
    return calculate(
        Filing(status="single", age_primary=age, age_spouse=0, dependents=[]),
        FederalIncome.model_validate(income),
        Deductions(),
        policy or TaxPolicy(year=2025, mode="package_law", annual_index=0),
    )
