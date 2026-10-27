"""Invented June departure retains worldwide US wages and post-move NJ-source wages."""

from wealthlab.tax.annual import AnnualCase
from wealthlab.tax.foreign_credit_example import synthetic as credit
from wealthlab.tax.foreign_tax_example import synthetic as household
from wealthlab.tax.nj_residence_income import to_income
from wealthlab.tax.nj_residence_inputs import NJResidencePlan


def profile():
    return NJResidencePlan.model_validate(
        dict(
            as_of="2025-12-31",
            people=[
                dict(
                    id="person_a",
                    role="primary",
                    status="part_year",
                    periods=[dict(start="2025-01-01", end="2025-07-01")],
                    residency_facts_assumed_confirmed=True,
                    us_citizen_full_year_assumed_confirmed=True,
                    source="Invented confirmed NJ domicile departure; travel is not the legal test",
                )
            ],
            income=[
                row("before_move", "2025-06-30", 50000, "allowed"),
                row("after_move_nj", "2025-09-30", 20000, "allowed"),
                row("after_move_foreign", "2025-09-30", 30000, "denied"),
            ],
            filing_election_assumed_confirmed=True,
            retirement_exclusions="denied",
            source="Synthetic independent NJ facts; no foreign-country residence conclusion",
        )
    )


def row(identity, received, amount, sourcing, kind="wages", owner="person_a"):
    return dict(
        id=identity,
        owner_id=owner,
        received=received,
        kind=kind,
        amount=str(amount),
        nj_source=sourcing,
        amount_and_classification_assumed_confirmed=True,
        source="Invented NJ amount/basis, date and source classification, independently confirmed",
    )


def synthetic():
    case = credit().annual
    state = profile()
    return AnnualCase.model_validate(
        case.model_copy(
            update=dict(
                nj_residence=state,
                nj_income=to_income(state),
            )
        ).model_dump()
    )


def household_example():
    scenario = household()
    case = scenario.tax_plan.cases[0].model_copy(update=dict(nj_residence=profile()))
    return scenario.model_copy(
        update=dict(tax_plan=scenario.tax_plan.model_copy(update=dict(cases=[case])))
    )
