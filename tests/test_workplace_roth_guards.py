"""Unknown participation/cost scope cannot silently produce tax-free plan cash."""

import pytest

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.retirement.workplace_roth_example import synthetic


@pytest.mark.parametrize(
    "field,value",
    [
        ("first_federal_contribution_year", None),
        ("first_federal_contribution_year", 2027),
        ("sources", ["cash"]),
        ("sources", ["work_roth", "work_roth"]),
        ("complete_vested_ordinary_designated_roth_contract_confirmed", False),
        ("no_inplan_conversions_inherited_loans_nua_or_other_special_history_confirmed", False),
        ("complete_cash_events_excluded_from_other_inputs_confirmed", False),
        ("independent_nj_basis_and_conditional_treatment_confirmed", False),
    ],
)
def test_incomplete_contract_history_fails_before_cash_moves(field, value):
    data = synthetic().model_dump(mode="json")
    data["workplace_plan"]["roth_cash_withdrawals"]["contracts"]["ordinary"][field] = value
    with pytest.raises(ValueError):
        project(Scenario.model_validate(data))


@pytest.mark.parametrize(
    "field,value",
    [
        ("source", "cash"),
        ("provenance", "unresolved"),
        ("date", "2026-02-02"),
        ("date", "2025-11-01"),
        ("id", "wlrmd_auto_alias"),
    ],
)
def test_unresolved_ineligible_or_aliasing_cash_orders_fail_closed(field, value):
    data = synthetic().model_dump(mode="json")
    data["workplace_plan"]["roth_cash_withdrawals"]["orders"][0][field] = value
    with pytest.raises(ValueError):
        project(Scenario.model_validate(data))
