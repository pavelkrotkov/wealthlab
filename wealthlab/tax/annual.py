"""One annual filing unit: federal and NJ liability plus explicit payment reconciliation."""

from decimal import Decimal
from typing import Literal

from pydantic import Field

from wealthlab.household.records import Money
from wealthlab.tax.facts import Deductions, FederalIncome, TaxModel
from wealthlab.tax.filing import Filing
from wealthlab.tax.foreign_credit_facts import ForeignCredits
from wealthlab.tax.nj_facts import NJDeductions, NJIncome
from wealthlab.tax.nj_residence_inputs import NJResidencePlan
from wealthlab.tax.policy import TaxPolicy


class Payments(TaxModel):
    federal_income_withheld: Money = Decimal(0)
    federal_estimates: Money = Decimal(0)
    employee_payroll_withheld: Money = Decimal(0)
    nj_withheld: Money = Decimal(0)
    nj_estimates: Money = Decimal(0)


class AnnualCase(TaxModel):
    filing: Filing
    nj_filing: Filing | None = None
    policy: TaxPolicy
    federal_income: FederalIncome
    federal_deductions: Deductions
    nj_income: NJIncome
    nj_deductions: NJDeductions
    nj_regime: Literal["published_2025", "freeze_2025"]
    payments: Payments = Field(default_factory=Payments)
    foreign_credits: ForeignCredits = Field(default_factory=ForeignCredits)
    nj_residence: NJResidencePlan | None = None


def evaluate(case: AnnualCase) -> dict:
    """Payments describe cash already paid; they never reduce taxable income twice."""
    from wealthlab.tax import federal, new_jersey, nj_residence, nj_residence_payments

    fed = federal.calculate(
        case.filing, case.federal_income, case.federal_deductions, case.policy, case.foreign_credits
    )
    state_engine = nj_residence.calculate if case.nj_residence is not None else new_jersey.calculate
    state_extra = dict(profile=case.nj_residence) if case.nj_residence is not None else {}
    nj = state_engine(
        case.nj_filing or case.filing,
        case.nj_income,
        case.nj_deductions,
        case.policy.year,
        assume_2025=case.nj_regime == "freeze_2025",
        **state_extra,
    )
    nj_residence_payments.validate(case, nj)
    # Employee payroll is reconciled separately from Form 1040 income-tax
    # payments. This preserves the same liability decomposition as the federal
    # adapter and exposes under/over-withholding without treating it as income.
    paid = case.payments
    fed_balance = fed["income_tax"] - paid.federal_income_withheld - paid.federal_estimates
    payroll_balance = fed["employee_payroll"] - paid.employee_payroll_withheld
    nj_balance = nj["income_tax"] - paid.nj_withheld - paid.nj_estimates
    return dict(
        federal=fed,
        new_jersey=nj,
        total_liability=fed["total"] + nj["income_tax"],
        federal_income_balance=fed_balance,
        payroll_balance=payroll_balance,
        nj_balance=nj_balance,
        total_balance=fed_balance + payroll_balance + nj_balance,
    )


def synthetic() -> AnnualCase:
    return AnnualCase(
        filing=Filing(status="joint", age_primary=40, age_spouse=40, dependents=[]),
        policy=TaxPolicy(year=2025, mode="package_law", annual_index=0),
        federal_income=FederalIncome(wages_primary=Decimal(200000)),
        federal_deductions=Deductions(),
        nj_income=NJIncome(wages=Decimal(200000)),
        nj_deductions=NJDeductions(),
        nj_regime="published_2025",
        payments=Payments(),
    )
