"""Synthetic loan/lapse case: zero termination cash can still create income tax."""

from wealthlab.products.life_contract_inputs import LifeContractCase
from wealthlab.tax.annual import synthetic as annual


def synthetic():
    baseline = annual().model_dump(mode="json")
    return LifeContractCase.model_validate(
        dict(
            synthetic=True,
            insurance_need="300000",
            retirement_date="2025-07-01",
            annual_cases={2025: baseline},
            contract=dict(
                id="policy",
                provenance="assumption",
                name="Synthetic personal policy",
                source="Synthetic educational case; no insurer terms",
                source_date="2025-01-01",
                start="2025-01-01",
                issue_date="2000-01-01",
                owner_birth_date="1970-01-01",
                opening_federal_basis="100000",
                opening_loan="120000",
                federal_status="non_mec",
                ordinary_personal_contract_confirmed=True,
                no_aggregation_or_special_basis_adjustments_confirmed=True,
                withdrawals_without_early_benefit_recapture_confirmed=True,
                capitalized_interest_is_new_loan_confirmed=True,
                additional_tax_exception="none",
                values_match_executed_events_confirmed=True,
                stop_funding_date=None,
                events=[
                    dict(
                        id="interest",
                        provenance="assumption",
                        date="2025-06-30",
                        kind="capitalized_interest",
                        amount="6000",
                        cash_value_before="126000",
                        nj_ordinary_income="0",
                    ),
                    dict(
                        id="lapse",
                        provenance="assumption",
                        date="2025-07-01",
                        kind="lapse",
                        amount="126000",
                        nj_ordinary_income="26000",
                    ),
                ],
                values=[
                    dict(
                        date="2025-01-01",
                        gross_cash_value="125000",
                        gross_surrender_value="123000",
                        gross_death_benefit="300000",
                    )
                ],
            ),
        )
    )
