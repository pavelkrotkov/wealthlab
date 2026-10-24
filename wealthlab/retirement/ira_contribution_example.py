"""A synthetic combined contribution, withdrawal and conversion cash book."""

from wealthlab.retirement.distribution_example import synthetic as withdrawals
from wealthlab.retirement.distribution_inputs import DistributionCase


def synthetic():
    data = withdrawals().model_dump(mode="json")
    data.update(opening_cash="10000", contribution_context_confirmed=True)
    data["contributions"] = dict(
        year=data["year"],
        rule_mode="published",
        filing="single",
        lived_with_spouse=False,
        spouse_covered_by_workplace_plan=False,
        opening_cash="10000",
        contributors=[
            dict(
                id="person",
                provenance="illustration",
                birth_date="1971-06-15",
                eligible_ira_compensation="100000",
                ira_compensation_budget="100000",
                traditional_ira_magi="100000",
                roth_ira_magi="100000",
                covered_by_workplace_plan=False,
                prior_employer_wages="0",
                workplace_compensation="0",
                workplace_eligible=False,
                catchup_permitted=False,
            )
        ],
        accounts=[{k: v for k, v in a.items() if k != "product"} for a in data["accounts"]],
        receipts=[],
        orders=[
            dict(
                id=f"deposit_{kind}",
                provenance="illustration",
                date="2026-01-15",
                owner="person",
                destination=destination,
                kind=kind,
                amount="3000",
            )
            for kind, destination in (("traditional_ira", "ira"), ("roth_ira", "roth"))
        ],
    )
    return DistributionCase.model_validate(data)
