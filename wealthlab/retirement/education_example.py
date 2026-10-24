"""Synthetic annual 529 case; no household records or actual plan holdings."""

from wealthlab.retirement.education_inputs import EducationCase


def synthetic():
    illustration = dict(provenance="illustration")
    return EducationCase.model_validate(
        dict(
            year=2026,
            opening_cash=12000,
            complete_context=True,
            nj_gross_income=180000,
            people=[
                dict(id="parent", household_cash_member=True, **illustration),
                dict(id="student", household_cash_member=False, **illustration),
            ],
            plans=[
                dict(
                    id="njbest",
                    njbest=True,
                    limits=[
                        dict(effective="2025-01-01", maximum_balance=305000),
                        dict(effective="2026-09-08", maximum_balance=525000),
                    ],
                    **illustration,
                )
            ],
            accounts=[
                dict(
                    id="college",
                    owner="parent",
                    beneficiary="student",
                    plan="njbest",
                    currency="USD",
                    wrapper="education",
                    balance=30000,
                    contribution_basis=20000,
                    monthly_fee=0,
                    **illustration,
                )
            ],
            **event_example(illustration),
            **expense_example(illustration),
        )
    )


def expense_example(illustration):
    return dict(
        expenses=[
            dict(
                id="tuition",
                beneficiary="student",
                paid="2026-12-01",
                amount=20000,
                tax_free_aid=3000,
                credit_expenses=4000,
                other_vehicle_expenses=1000,
                eligibility="confirmed_higher_education",
                **illustration,
            )
        ],
        allocations=[
            dict(
                id="parent_uses",
                account="college",
                recipient="owner",
                expenses=[dict(expense="tuition", amount=10000)],
                **illustration,
            ),
            dict(
                id="student_uses",
                account="college",
                recipient="beneficiary",
                expenses=[dict(expense="tuition", amount=2000)],
                nj_recaptured_contributions=0,
                **illustration,
            ),
        ],
    )


def event_example(illustration):
    return dict(
        contributions=[
            dict(
                id="save",
                date="2026-01-02",
                destination="college",
                amount=15000,
                **illustration,
            )
        ],
        returns=[
            dict(
                id="growth",
                date="2026-06-01",
                account_id="college",
                rate="0.10",
                **illustration,
            )
        ],
        withdrawals=[
            dict(
                id="reimburse",
                date="2026-08-01",
                source="college",
                amount=15000,
                payee="owner",
                **illustration,
            ),
            dict(
                id="student_cash",
                date="2026-09-01",
                source="college",
                amount=5000,
                payee="beneficiary",
                **illustration,
            ),
        ],
    )
