"""Unsupported combinations fail before any IRA can fund the household."""

from datetime import date

import pytest

from wealthlab.household.projection import project
from wealthlab.retirement.ira_household_example import synthetic


@pytest.mark.parametrize(
    "flag",
    ["complete_ordinary_ira_pools_confirmed", "other_tax_inputs_exclude_ira_events_confirmed"],
)
def test_confirmations_are_required(flag):
    c = synthetic()
    plan = c.ira_plan.model_copy(update={flag: False})
    with pytest.raises(ValueError, match="Confirm complete"):
        project(c.model_copy(update=dict(ira_plan=plan)))


@pytest.mark.parametrize(
    "change,match",
    [
        (dict(start=date(2026, 2, 1)), "complete calendar years"),
        (dict(tax_plan=None), "explicit tax plan"),
    ],
)
def test_required_household_context(change, match):
    with pytest.raises(ValueError, match=match):
        project(synthetic().model_copy(update=change))


def test_monthly_accrued_tax_cannot_use_unfinalized_annual_basis():
    c = synthetic()
    plan = c.tax_plan.model_copy(update=dict(settlement_timing="monthly_accrued"))
    with pytest.raises(ValueError, match="year-end settlement"):
        project(c.model_copy(update=dict(tax_plan=plan)))


def test_ira_owners_cannot_swap_household_payroll_or_history():
    c = synthetic()
    plan = c.ira_plan.model_copy(update=dict(owners=list(reversed(c.ira_plan.owners))))
    with pytest.raises(ValueError, match="filing order"):
        project(c.model_copy(update=dict(ira_plan=plan)))
