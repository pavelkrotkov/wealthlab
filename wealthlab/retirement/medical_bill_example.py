"""A synthetic medical bill creates a real shortfall, arrears and paid-only receipts."""

from wealthlab.household.example import synthetic as household
from wealthlab.household.scenario import Scenario
from wealthlab.retirement.hsa_household_example import context
from wealthlab.retirement.hsa_household_inputs import HSAPlan
from wealthlab.tax.facts import FederalIncome
from wealthlab.tax.nj_facts import NJIncome
from wealthlab.tax.projection_example import template
from wealthlab.tax.projection_inputs import TaxEvent


def synthetic():
    data = household().model_dump(mode="json")
    data.update(
        name="Synthetic current medical bill, arrears and HSA payments",
        incomes=[],
        expenses=[],
        contributions=[],
        accounts=[
            dict(
                id="cash",
                owner="joint",
                wrapper="cash",
                balance=1000,
                provenance="illustration",
                currency="USD",
                monthly_fee=0,
            ),
            dict(
                id="cash_hsa",
                owner="person_a",
                wrapper="hsa",
                balance=3000,
                provenance="illustration",
                currency="USD",
                monthly_fee=0,
            ),
        ],
    )
    scenario = Scenario.model_validate(data)
    taxes = template(scenario)
    taxes = taxes.model_copy(
        update=dict(
            events=[
                TaxEvent(
                    date="2026-02-01",
                    description="Supplied nonincome gift receipt",
                    cash_received=3000,
                    federal=FederalIncome(),
                    new_jersey=NJIncome(),
                )
            ]
        )
    )
    return scenario.model_copy(update=dict(tax_plan=taxes, hsa_plan=plan(scenario)))


def plan(scenario):
    return HSAPlan(
        years=[context(scenario, year) for year in (2026, 2027)],
        medical_receipts=[],
        interest=[],
        contributions=[
            dict(
                id="employer",
                provenance="illustration",
                date="2026-03-01",
                destination="cash_hsa",
                source="direct_employer",
                amount=5000,
            )
        ],
        withdrawals=[
            dict(
                id=f"later_{year}",
                provenance="illustration",
                date=f"{year}-03-15",
                source="cash_hsa",
                amount=3000,
                mode="qualified_only",
                receipt_ids=["care"],
            )
            for year in (2026, 2027)
        ],
        medical_bills=[
            dict(
                id="care",
                provenance="illustration",
                incurred="2026-01-10",
                date="2026-01-15",
                amount=6000,
                eligible_owners=["person_a"],
                eligibility="qualified_medical",
                hsa_source="cash_hsa",
                hsa_amount=5000,
            )
        ],
        bill_expenses_excluded_from_other_inputs_confirmed=True,
        nj_treatment="taxable_bank_interest_assumption",
        conditional_nj_treatment_confirmed=True,
        cash_only_accounts_and_complete_context_confirmed=True,
        receipts_paid_before_projection_confirmed=True,
        employer_funding_excluded_from_other_nj_wages_confirmed=True,
        priority="after_receipts_before_ira_and_current_tax",
    )
