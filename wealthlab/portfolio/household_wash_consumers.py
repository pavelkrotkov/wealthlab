"""Revised returns update eligibility and future lookbacks, never old bills.

IRA elections retain their posted deduction and nondeductible basis. A larger
permitted deduction is not silently claimed; an overclaim or excessive Roth
contribution still blocks the result. Medicare records replace the original
household return by identity for future lookbacks, while education audits use
the corrected final NJ gross income. Already billed redeterminations require
separate billing logic and cannot be rewritten as if no cash had moved.
"""

from wealthlab.retirement.education_nj import deduction
from wealthlab.retirement.ira_contribution_tax import check_completed


def check_ira(ira, year, annual, result):
    if not hasattr(ira, "closed_years") or year not in ira.closed_years:
        return None
    context, rows, additions = ira.closed_years[year]
    return check_completed(
        context, rows, additions, annual.federal_income, result["federal"], allow_underclaim=True
    )


def medicare_revision(medicare, year, result, when):
    if medicare is None:
        return
    identity = f"household_return_{year}"
    old = next((i for i in medicare.case.income_history if i.id == identity), None)
    if old is None or old.agi == result["federal"]["agi"]:
        return
    validate_billing(medicare.case, identity, when)
    revised = old.model_copy(update=dict(agi=result["federal"]["agi"]))
    return medicare.case.model_copy(
        update=dict(
            income_history=[
                revised if i.id == identity else i for i in medicare.case.income_history
            ]
        )
    )


def update_education(education, year, result, reason="january_wash_reconciliation"):
    if education is None:
        return
    for annual in education.years:
        if annual["year"] == year:
            annual["njbest_potential_deduction"] = deduction(
                result["new_jersey"]["gross_income"], annual["njbest_funded_contributions"]
            )
            annual["income_finalized"] = reason


def validate_billing(case, identity, when):
    if any(d.income == identity and d.premium_year <= when.year for d in case.determinations):
        raise ValueError(
            "Revising an already billed Medicare redetermination needs a billing adapter."
        )
