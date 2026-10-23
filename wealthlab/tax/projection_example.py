"""Create an explicit editable tax-plan template; no private eligibility is inferred."""

from datetime import date, timedelta
from decimal import Decimal

from wealthlab.tax.annual import AnnualCase
from wealthlab.tax.facts import Deductions, FederalIncome
from wealthlab.tax.filing import Filing
from wealthlab.tax.nj_facts import NJDeductions, NJIncome
from wealthlab.tax.policy import TaxPolicy
from wealthlab.tax.projection_inputs import IncomeRule, TaxPlan


def template(scenario) -> TaxPlan:
    """Template assumes wages and frozen 2025 law; UI requires explicit opt-in/editing."""
    years = range(scenario.start.year, (scenario.end - timedelta(days=1)).year + 1)
    cases = [annual_case(scenario, year) for year in years]
    primary = scenario.members[0].id
    rules = [
        IncomeRule(
            income_id=item.id,
            federal="wages_primary" if item.owner == primary else "wages_spouse",
            new_jersey="wages",
        )
        for item in scenario.incomes
    ]
    return TaxPlan(
        cases=cases,
        income_rules=rules,
        federal_wage_withholding=Decimal(".20"),
        nj_wage_withholding=Decimal(".06"),
    )


def annual_case(scenario, year: int) -> AnnualCase:
    ages = [age(member.birth_date, year) for member in scenario.members]
    filing = Filing(
        status="joint" if len(ages) == 2 else "single",
        age_primary=ages[0],
        age_spouse=ages[1] if len(ages) == 2 else 0,
        dependents=[],
    )
    federal_ages = [age(member.birth_date, year, federal=True) for member in scenario.members]
    federal = filing.model_copy(
        update={
            "age_primary": federal_ages[0],
            "age_spouse": federal_ages[1] if len(ages) == 2 else 0,
        }
    )
    return AnnualCase(
        filing=federal,
        nj_filing=filing,
        policy=TaxPolicy(year=year, mode="freeze_2025", annual_index=0),
        federal_income=FederalIncome(),
        federal_deductions=Deductions(),
        nj_income=NJIncome(),
        nj_deductions=NJDeductions(),
        nj_regime="freeze_2025",
    )


def age(born: date, year: int, federal: bool = False) -> int:
    return year - born.year + int(federal and born.month == 1 and born.day == 1)
