"""A synthetic age-55 IRA withdrawal, conversion and Roth-bucket consumption."""

from wealthlab.retirement.distribution_inputs import DistributionCase
from wealthlab.tax.annual import synthetic as tax_example


def synthetic():
    annual = tax_example().model_dump(mode="json")
    annual["policy"].update(year=2026, mode="freeze_2025")
    annual["nj_regime"] = "freeze_2025"
    annual["filing"].update(status="single", age_primary=55, age_spouse=0)
    annual["federal_income"]["wages_primary"] = "100000.00"
    annual["nj_income"]["wages"] = "100000.00"
    return DistributionCase.model_validate(
        dict(
            year=2026,
            opening_cash="0.00",
            opening_context_complete=True,
            accounts=accounts(),
            nj_treatment="resident_combined_owner_pools",
            rmd_policy="december_target_no_deferral",
            annual_tax_case=annual,
            owners=owners(),
            orders=[
                dict(
                    id=f"draw_{i}",
                    provenance="assumption",
                    date=when,
                    source=source,
                    destination=target,
                    kind=kind,
                    amount=amount,
                    early_penalty_exception=False,
                )
                for i, (when, source, target, kind, amount) in enumerate(
                    [
                        ("2026-06-01", "ira", None, "withdrawal", "10000.00"),
                        ("2026-07-01", "ira", "roth", "conversion", "20000.00"),
                        ("2026-08-01", "roth", None, "withdrawal", "25000.00"),
                    ]
                )
            ],
        )
    )


def accounts():
    return [
        dict(
            id=key,
            provenance="assumption",
            owner="person",
            currency="USD",
            wrapper=wrapper,
            product=product,
            balance=balance,
            monthly_fee="0.00",
        )
        for key, wrapper, product, balance in [
            ("ira", "traditional", "traditional_ira", "100000.00"),
            ("roth", "roth", "roth_ira", "50000.00"),
        ]
    ]


def owners():
    return [
        dict(
            id="person",
            provenance="assumption",
            birth_date="1971-06-15",
            federal_ira_basis="20000.00",
            nj_ira_basis="50000.00",
            roth_regular_basis="10000.00",
            nj_roth_basis="30000.00",
            roth_first_year=2010,
            rmd_table="uniform",
            conversions=[
                dict(year=2023, taxable_remaining="15000.00", nontaxable_remaining="5000.00")
            ],
        )
    ]
