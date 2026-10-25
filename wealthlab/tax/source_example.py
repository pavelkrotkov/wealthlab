"""Synthetic pension withholding cannot fund an optional HSA deposit.

A payer distributes $10,000: $2,000 goes straight to the tax authority and
$8,000 reaches the household. A requested $8,500 HSA deposit funds only $8,000.
The unused tax credit is received the following April, not on the pension date.
"""

from wealthlab.household.example import synthetic as household
from wealthlab.household.scenario import Scenario
from wealthlab.retirement.medical_bill_example import plan
from wealthlab.tax.facts import FederalIncome
from wealthlab.tax.nj_facts import NJIncome
from wealthlab.tax.projection_example import template
from wealthlab.tax.projection_inputs import TaxEvent
from wealthlab.tax.source_withholding import SourceWithholding


def synthetic():
    data = household().model_dump(mode="json")
    data.update(
        name="Synthetic pension withholding and HSA cash constraint",
        incomes=[],
        expenses=[],
        contributions=[],
        accounts=[
            dict(
                id="cash",
                owner="joint",
                wrapper="cash",
                balance=0,
                provenance="illustration",
                currency="USD",
                monthly_fee=0,
            ),
            dict(
                id="cash_hsa",
                owner="person_a",
                wrapper="hsa",
                balance=0,
                provenance="illustration",
                currency="USD",
                monthly_fee=0,
            ),
        ],
    )
    scenario = Scenario.model_validate(data)
    taxes = template(scenario).model_copy(update=dict(events=[pension()]))
    hsa_data = plan(scenario).model_dump(mode="json")
    hsa_data.update(
        medical_bills=[],
        withdrawals=[],
        contributions=[
            dict(
                id="personal",
                provenance="illustration",
                date="2026-02-01",
                destination="cash_hsa",
                source="personal_cash",
                amount=8500,
            )
        ],
    )
    from wealthlab.retirement.hsa_household_inputs import HSAPlan

    hsa = HSAPlan.model_validate(hsa_data)
    return scenario.model_copy(update=dict(tax_plan=taxes, hsa_plan=hsa))


def pension():
    return TaxEvent(
        date="2026-02-01",
        description="Synthetic external pension, tax withheld by payer",
        cash_received=8000,
        federal=FederalIncome(taxable_pension=10000),
        new_jersey=NJIncome(pension=10000),
        withholding=SourceWithholding(gross_cash=10000, federal_income_withheld=2000),
    )
