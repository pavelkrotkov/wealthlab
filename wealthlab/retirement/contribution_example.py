"""Independent synthetic high-earner and cash-constrained contribution case."""

from wealthlab.retirement.contribution_inputs import ContributionCase


def data():
    assumed = dict(provenance="assumption")
    return dict(
        year=2026,
        filing="single",
        lived_with_spouse=False,
        spouse_covered_by_workplace_plan=False,
        opening_cash="40000.00",
        contributors=[
            dict(
                assumed,
                id="person",
                birth_date="1965-06-15",
                eligible_ira_compensation="200000.00",
                ira_compensation_budget="200000.00",
                workplace_compensation="200000.00",
                traditional_ira_magi="200000.00",
                roth_ira_magi="200000.00",
                covered_by_workplace_plan=True,
                prior_employer_wages="200000.00",
                workplace_eligible=True,
                catchup_permitted=True,
            )
        ],
        accounts=accounts(),
        orders=[
            dict(
                assumed,
                id=f"order_{i}",
                date="2026-01-15",
                owner="person",
                destination=destination,
                kind=kind,
                amount=amount,
            )
            for i, (destination, kind, amount) in enumerate(
                [
                    ("pretax", "pretax_401k", "35750.00"),
                    ("roth", "roth_401k", "11250.00"),
                    ("ira", "traditional_ira", "8600.00"),
                    ("rothira", "roth_ira", "8600.00"),
                ]
            )
        ],
    )


def synthetic():
    return ContributionCase.model_validate(data())


def accounts():
    return [
        dict(
            provenance="assumption",
            id=key,
            owner="person",
            currency="USD",
            wrapper=wrapper,
            balance="0.00",
            monthly_fee="0.00",
        )
        for key, wrapper in [
            ("pretax", "traditional"),
            ("roth", "roth"),
            ("ira", "traditional"),
            ("rothira", "roth"),
        ]
    ]
