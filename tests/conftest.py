"""Set cache paths before numerical packages are imported during collection."""

from wealthlab.runtime import configure

configure()

import pytest  # noqa: E402

from wealthlab.household.example import synthetic  # noqa: E402


@pytest.fixture
def payload():
    return synthetic().model_dump(mode="json")


@pytest.fixture
def itemizer(payload):
    """A synthetic December itemizer with typed opening income and cash facts."""
    from decimal import Decimal as D

    from wealthlab.household.scenario import Scenario
    from wealthlab.tax.annual import Payments
    from wealthlab.tax.facts import Deductions, FederalIncome
    from wealthlab.tax.nj_facts import NJIncome
    from wealthlab.tax.projection_example import template

    def build(cash="100000", end="2027-01-01", nj_paid="0"):
        payload.update(start="2026-12-01", end=end, incomes=[], expenses=[])
        payload["accounts"][0]["balance"] = cash
        household = Scenario.model_validate(payload)
        plan = template(household)
        opening = plan.cases[0].model_copy(
            update={
                "federal_income": FederalIncome(wages_primary=D(200000)),
                "nj_income": NJIncome(wages=D(200000)),
                "federal_deductions": Deductions(qualified_mortgage_interest=D(30000)),
                "payments": Payments(
                    employee_payroll_withheld=D("13818.20"), nj_withheld=D(nj_paid)
                ),
            }
        )
        plan = plan.model_copy(update={"cases": [opening, *plan.cases[1:]]})
        return household.model_copy(update={"tax_plan": plan})

    return build
