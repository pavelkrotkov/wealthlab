"""Only actual funded Roth payroll creates cost or a first participation year."""

import pytest
from workplace_roth_cases import payroll_data

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario


def test_funded_roth_deferrals_create_actual_principal_and_start_the_plan_clock():
    rows = project(Scenario.model_validate(payroll_data(10000)))
    january = rows[0]["workplace_roth_contracts"][0]
    assert january["first_federal_contribution_year"] == 2026
    assert january["federal_basis"] == january["nj_basis"] == 2000
    assert rows[0]["workplace_contributions"] == 2000
    cash = rows[-1]["workplace_roth_audit"][0]
    assert cash["gross"] == cash["federal_basis_recovered"] == 2000
    assert cash["federal_taxable"] == 0
    assert not cash["federal_qualified"]


def test_forecast_eligibility_without_current_wages_creates_no_basis_or_clock():
    rows = project(Scenario.model_validate(payroll_data(0)))
    january = rows[0]["workplace_roth_contracts"][0]
    assert january["first_federal_contribution_year"] is None
    assert january["federal_basis"] == 0
    assert rows[0]["workplace_contributions"] == 0
    assert rows[-1]["workplace_roth_audit"][0]["gross"] == 0


def test_later_employee_deferrals_cannot_reopen_a_separated_cash_contract():
    data = payroll_data(10000)
    data["workplace_plan"]["orders"][0]["date"] = "2026-03-01"
    with pytest.raises(ValueError, match="cannot reopen a separated Roth"):
        project(Scenario.model_validate(data))
