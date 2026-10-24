"""A one-year cash-HSA household isolates funded amounts and conditional tax ingredients."""

from wealthlab.household.scenario import Scenario
from wealthlab.retirement.hsa_household_example import synthetic
from wealthlab.tax.projection_example import template


def flat(balance=10000, requested=5000, nj_fraction="0"):
    data = synthetic().model_dump(mode="json")
    data.update(end="2027-01-01", incomes=[], expenses=[], contributions=[], ira_plan=None)
    data["accounts"] = [a for a in data["accounts"] if a["id"] in ("cash", "cash_hsa")]
    for account in data["accounts"]:
        account["balance"] = str(balance if account["wrapper"] == "hsa" else 100000)
    plan = data["hsa_plan"]
    plan.update(
        years=plan["years"][:1],
        contributions=[],
        interest=[],
        medical_receipts=[],
        withdrawals=[
            dict(
                id="draw",
                provenance="assumption",
                date="2026-03-01",
                source="cash_hsa",
                amount=str(requested),
                mode="allow_nonqualified",
                receipt_ids=[],
            )
        ],
        nonqualified_treatment="ordinary_noninvestment_assumption",
        nj_withdrawal_taxable_fractions=dict(draw=nj_fraction),
        generated_distribution_tax_excluded_from_other_inputs_confirmed=True,
    )
    case = Scenario.model_validate(data)
    return case.model_copy(update=dict(tax_plan=template(case)))


def change(case, modify):
    data = case.model_dump(mode="json")
    modify(data)
    return Scenario.model_validate(data)
