"""Illustrate actual nonqualified cash with independently supplied federal and NJ assumptions."""

from wealthlab.household.scenario import Scenario
from wealthlab.retirement.hsa_household_example import synthetic as qualified_household


def synthetic():
    data = qualified_household().model_dump(mode="json")
    data["name"] = "Synthetic cash HSA nonqualified distribution and tax assumptions"
    plan = data["hsa_plan"]
    plan["withdrawals"].append(
        dict(
            id="nonmedical_cash",
            provenance="illustration",
            date="2026-12-01",
            source="cash_hsa",
            amount="10000",
            mode="allow_nonqualified",
            receipt_ids=[],
        )
    )
    plan.update(
        nonqualified_treatment="ordinary_noninvestment_assumption",
        nj_withdrawal_taxable_fractions=dict(nonmedical_cash="0"),
        generated_distribution_tax_excluded_from_other_inputs_confirmed=True,
    )
    return Scenario.model_validate(data)
