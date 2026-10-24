"""Synthetic spouses share family capacity; one begins Medicare midyear."""

from wealthlab.retirement.hsa_inputs import HSACase


def synthetic():
    return HSACase.model_validate(
        dict(
            year=2026,
            opening_cash="2000.00",
            married=True,
            complete_context=True,
            contribution_policy="monthly_only",
            nj_treatment="unconfirmed",
            owners=[
                owner("person", "1966-08-31", "2018-01-01", 13),
                owner("spouse", "1961-07-01", "2019-01-01", 7),
            ],
            accounts=[
                account("hsa", "person", "10000.00"),
                account("spouse_hsa", "spouse", "5000.00"),
            ],
            contributions=[
                dict(
                    id="employer",
                    provenance="assumption",
                    date="2026-01-10",
                    destination="hsa",
                    source="direct_employer",
                    amount="2000.00",
                ),
                dict(
                    id="personal",
                    provenance="assumption",
                    date="2026-01-11",
                    destination="hsa",
                    source="personal_cash",
                    amount="8000.00",
                ),
                dict(
                    id="spouse_contribution",
                    provenance="assumption",
                    date="2026-01-12",
                    destination="spouse_hsa",
                    source="personal_cash",
                    amount="3000.00",
                ),
            ],
            interest=[
                dict(
                    id="interest",
                    provenance="assumption",
                    date="2026-06-15",
                    account_id="hsa",
                    taxable_bank_interest="100.00",
                )
            ],
            medical_receipts=receipts(),
            withdrawals=withdrawals(),
        )
    )


def owner(identity, birth, established, medicare_month):
    return dict(
        id=identity,
        provenance="assumption",
        birth_date=birth,
        established=established,
        months=[
            dict(
                month=month,
                coverage="family",
                disqualifying_coverage=False,
                medicare=month >= medicare_month,
                claimable_dependent=False,
            )
            for month in range(1, 13)
        ],
    )


def account(identity, owner_id, balance):
    return dict(
        id=identity,
        provenance="assumption",
        owner=owner_id,
        currency="USD",
        wrapper="hsa",
        monthly_fee="0.00",
        balance=balance,
    )


def receipts():
    return [
        dict(
            id="medical",
            provenance="assumption",
            eligible_owners=["person", "spouse"],
            incurred="2020-01-01",
            paid="2021-01-01",
            amount="3000.00",
            reimbursed_elsewhere="1000.00",
            deducted_federally="500.00",
            eligibility="qualified_medical",
        ),
        dict(
            id="before_establishment",
            provenance="assumption",
            eligible_owners=["person"],
            incurred="2010-01-01",
            paid="2010-01-01",
            amount="2000.00",
            reimbursed_elsewhere="0.00",
            deducted_federally="0.00",
            eligibility="qualified_medical",
        ),
    ]


def withdrawals():
    return [
        dict(
            id=identity,
            provenance="assumption",
            date=when,
            source=source,
            amount=amount,
            mode=mode,
            receipt_ids=ids,
        )
        for identity, when, source, amount, mode, ids in [
            ("qualified", "2026-07-01", "hsa", "2000.00", "qualified_only", ["medical"]),
            ("after_65", "2026-07-02", "spouse_hsa", "1000.00", "allow_nonqualified", ["medical"]),
            (
                "early",
                "2026-08-01",
                "hsa",
                "2000.00",
                "allow_nonqualified",
                ["before_establishment"],
            ),
        ]
    ]
