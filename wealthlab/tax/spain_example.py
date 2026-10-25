"""Original supplied profiles; Toledo's income/IP numbers are an attributed official oracle."""

from wealthlab.tax.spain_inputs import SpainCase
from wealthlab.tax.spain_regional_policy import policy

SOURCE = "Original synthetic assumption; classifications are independently supplied"


def amount(value, when="2025-12-31", currency="EUR", rate="1"):
    return dict(amount=str(value), currency=currency, date=when, eur_per_unit=rate, source=SOURCE)


def income(identity, value, base):
    return dict(
        id=identity,
        kind="income",
        owner_id="synthetic_person",
        source_country="US",
        product="ordinary",
        spanish_base=base,
        treatment="allowed",
        classification_source="Supplied post-limitation recognized amount; no raw loss netting",
        treaty_treatment="none",
        treaty_source="No treaty exemption or bilateral credit claimed in this example",
        amount=amount(value),
    )


def asset(identity, value, nonproductive):
    return dict(
        id=identity,
        owner_id="synthetic_person",
        ownership_share="1",
        product="ordinary",
        kind="financial" if not nonproductive else "other",
        fiscal_value=amount(value),
        fiscal_valuation_source="Supplied December31 statutory fiscal value",
        treatment="included",
        exemption_eur="0",
        classification_source=SOURCE,
        nonproductive=nonproductive,
    )


def synthetic(region="castilla_la_mancha"):
    return SpainCase.model_validate(
        dict(
            synthetic=True,
            person_id="synthetic_person",
            year=2025,
            as_of="2026-07-31",
            policy="published_2025",
            citizenship="us",
            residence="full_year_resident",
            residence_source="Synthetic full-year ordinary resident assumption",
            region=region,
            filing="individual",
            worldwide_inputs_complete_confirmed=True,
            recognition_prelimited_confirmed=True,
            incomes=[income("general", 50000, "general"), income("savings", 2000, "savings")],
            general_reduction_eur="2000",
            savings_reduction_eur="0",
            state_minimum_eur="5550",
            regional_minimum_eur=policy(region)["ordinary_under65_minimum"],
            allowance_source="Supplied under65/no dependents minima and prelimited reduction",
            assets=[asset("productive", 7750000, False), asset("nonproductive", 250000, True)],
            debts=[],
            long_held_gain_cap_exclusion_eur="1000",
            patrimonial_company_dividends_eur="0",
            cap_adjustment_source="Supplied post-netting long-held disposal exclusion",
            credits=dict(
                irpf_state="0",
                irpf_regional="0",
                wealth_foreign="0",
                wealth_regional="0",
                solidarity_foreign="0",
                source="No independently eligible tax credit supplied",
            ),
            payments=[],
        )
    )
