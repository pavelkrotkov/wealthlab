"""Age/disability exceptions remove additional tax while leaving actual ordinary income."""

import pytest
from hsa_distribution_cases import change, flat

from wealthlab.household.projection import project
from wealthlab.tax.projection_example import template


@pytest.mark.parametrize("disabled,additional", [(None, 200), ("2026-07-01", 0)])
def test_actual_distribution_dates_apply_the_existing_age_and_disability_exceptions(
    disabled, additional
):
    def configure(data):
        member = data["members"][0]
        member["birth_date"] = "1961-07-15"
        plan = data["hsa_plan"]
        owner = plan["years"][0]["owners"][0]
        owner.update(birth_date=member["birth_date"], disabled_since=disabled)
        plan["withdrawals"] = [
            dict(
                id=f"draw_{day}",
                provenance="assumption",
                date=f"2026-07-{day}",
                source="cash_hsa",
                amount="1000",
                mode="allow_nonqualified",
                receipt_ids=[],
            )
            for day in ("14", "15")
        ]
        plan["nj_withdrawal_taxable_fractions"] = dict(draw_14="0", draw_15="0")

    case = change(flat(), configure)
    rows = project(case.model_copy(update=dict(tax_plan=template(case))))
    assert sum(r["hsa_nonqualified_taxable"] for r in rows) == 2000
    assert sum(r["hsa_additional_tax"] for r in rows) == additional
    assert rows[-1]["annual_tax"]["federal"]["agi"] == 2000
    assert rows[-1]["annual_tax"]["total_liability"] == additional
