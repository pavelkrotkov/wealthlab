"""Public synthetic covered wages, known source allocation and one observed foreign payment."""

from wealthlab.tax.annual import synthetic as annual
from wealthlab.tax.foreign_credit_inputs import ForeignCreditCase


def amount(when, native, currency="USD", rate="1"):
    return dict(
        date=when,
        amount=str(native),
        currency=currency,
        usd_per_unit=rate,
        fx_source="Invented dated spot quote for a reproducible synthetic case",
    )


def synthetic():
    base = annual().model_dump(mode="json")
    base["filing"].update(status="single", age_spouse=0)
    base["federal_income"]["wages_primary"] = "100000"
    base["nj_income"]["wages"] = "100000"
    base["payments"].update(federal_income_withheld="5000", employee_payroll_withheld="7650")
    incomes = [
        dict(
            id=identity,
            owner_id="person_a",
            country=country,
            kind="wages",
            basket="general",
            value=amount("2025-06-30", 50000),
            source_classification="Assumed US-covered employer wages, independently sourced",
        )
        for identity, country in [("work_us", "US"), ("work_es", "ES")]
    ]
    paid = dict(
        id="es_paid",
        owner_id="person_a",
        country="ES",
        liability_year=2025,
        tax_type="income",
        kind="payment",
        basket="general",
        value=amount("2025-12-15", 10000, "EUR", "1.10"),
        creditable_native="10000",
        eligibility="allowed",
        included_income_confirmed=True,
        income_ids=["work_es"],
        source="Assumed independently creditable synthetic income tax, not a filing decision",
    )
    return ForeignCreditCase.model_validate(
        dict(
            synthetic=True,
            annual=base,
            as_of="2025-12-31",
            people={"person_a": "primary"},
            income=incomes,
            tax_cash=[paid],
            opening_carries=[],
            eligibility="allowed",
            ordinary_source_and_tax_allocation_confirmed=True,
            carry_filing_unit_continuity_confirmed=True,
            prior_year_carryback_capacity_reviewed_zero_confirmed=True,
            source="Synthetic ordinary profile; independently assumed zero2024 carryback capacity",
        )
    )
