"""A confirmed $20,000 plan receipt adds separate basis without adding IRA spending cash.

Opening IRA value10k has federal1k/NJ2k basis. Incoming20k carries4k/6k;
annual basis is5k/8k. A later15k withdrawal from total30k recovers2.5k/4k,
leaving federal12.5k and NJ11k taxable with2.5k/4k basis carried onward.
"""

from wealthlab.retirement.distribution_example import synthetic as withdrawals
from wealthlab.retirement.distribution_inputs import DistributionCase


def synthetic():
    data = withdrawals().model_dump(mode="json")
    data["accounts"][0]["balance"] = 10000
    data["accounts"][1]["balance"] = 0
    data["owners"][0].update(
        birth_date="1960-06-15",
        federal_ira_basis=1000,
        nj_ira_basis=2000,
        roth_regular_basis=0,
        nj_roth_basis=0,
        conversions=[],
    )
    data["annual_tax_case"]["filing"]["age_primary"] = 66
    if data["annual_tax_case"]["nj_filing"] is not None:
        data["annual_tax_case"]["nj_filing"]["age_primary"] = 66
    data["orders"] = data["orders"][:1]
    data["orders"][0].update(amount=15000)
    data["incoming_rollovers"] = [receipt()]
    return DistributionCase.model_validate(data)


def receipt():
    return dict(
        id="direct_plan_receipt",
        provenance="illustration",
        date="2026-03-01",
        owner="person",
        source="external_plan",
        destination="ira",
        amount=20000,
        federal_basis_transferred=4000,
        nj_basis_transferred=6000,
        profile="ordinary_qualified_plan_cash_to_same_owner_traditional_ira",
        eligible_direct_rollover_and_rmd_excluded_confirmed=True,
        independent_basis_and_no_special_features_confirmed=True,
        excluded_from_opening_balances_and_cash_receipts_confirmed=True,
    )
