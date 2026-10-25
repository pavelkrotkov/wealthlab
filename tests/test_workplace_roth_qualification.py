"""Five taxable years and exact half-birthday are independent of the plan age55 exception."""

import pytest
from workplace_roth_cases import aged_data

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario


@pytest.mark.parametrize("when,qualified", [("2026-01-01", False), ("2026-02-01", True)])
def test_exact_age59_half_boundary(when, qualified):
    data = aged_data("1966-08-01")
    plan = data["workplace_plan"]["roth_cash_withdrawals"]
    plan["contracts"]["ordinary"]["separation_date"] = "2020-12-01"
    plan["orders"][0]["date"] = when
    row = project(Scenario.model_validate(data))[-1]["workplace_roth_audit"][0]
    assert row["federal_qualified"] == qualified
    assert row["federal_taxable"] == (0 if qualified else 300)
    assert row["additional_tax"] == (0 if qualified else 30)


@pytest.mark.parametrize("first,qualified", [(2021, True), (2022, False)])
def test_five_tax_year_boundary_after_reaching_age59_half(first, qualified):
    data = aged_data("1960-07-01")
    data["workplace_plan"]["roth_cash_withdrawals"]["contracts"]["ordinary"][
        "first_federal_contribution_year"
    ] = first
    row = project(Scenario.model_validate(data))[-1]["workplace_roth_audit"][0]
    assert row["federal_qualified"] == qualified
    assert row["federal_taxable"] == (0 if qualified else 300)
    assert row["additional_tax"] == 0
