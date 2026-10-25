"""Unsupported legal profiles and malformed dates fail before investor cash is touched."""

import pytest
from household_sleeve_cases import change
from private_fund_cases import fund, request

from wealthlab.household.projection import project


@pytest.mark.parametrize(
    "field",
    [
        "eligibility_assumed_confirmed",
        "limited_liability_no_calls_assumed_confirmed",
        "cash_only_no_hot_assets_no_liability_changes_assumed_confirmed",
        "tax_basis_schedule_complete_assumed_confirmed",
    ],
)
def test_unconfirmed_contract_is_rejected(field):
    with pytest.raises(ValueError, match="Confirm eligibility"):
        project(fund(**{field: False}))


@pytest.mark.parametrize(
    "updates,match",
    [
        (dict(exit_at_horizon=True), "Fund exits"),
        (dict(margin_policy="top_up_then_liquidate"), "margin is internal"),
    ],
)
def test_generic_margin_and_exit_policy_cannot_bypass_the_contract(updates, match):
    def configure(data):
        data["sleeve_plan"]["sleeves"][0]["case"].update(updates)

    with pytest.raises(ValueError, match=match):
        project(change(fund(), configure))


def test_negative_basis_is_never_silently_clamped():
    adjustment = dict(
        id="invalid_basis",
        provenance="assumption",
        date="2026-01-01",
        federal="-100001",
        new_jersey=0,
        explanation="Invalid assumed adjustment",
    )
    with pytest.raises(ValueError, match="negative"):
        project(fund(basis_adjustments=[adjustment]))


def test_notice_outside_projection_is_rejected():
    with pytest.raises(ValueError, match="notices"):
        project(fund(requests=[request(notice="2025-12-01")]))


def test_zero_gate_is_rejected_before_any_household_execution():
    with pytest.raises(ValueError, match="greater than 0"):
        project(fund(gate_fraction="0"))
