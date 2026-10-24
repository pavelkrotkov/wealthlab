"""Ownership, opening value and seller identity cannot silently diverge.

A linked account is the same capital already on the household balance sheet.
Explicit confirmations do not excuse a mismatched owner, missing price month
or second liquidation adapter. Reusing a saved case must not reuse mutable
lot-book state from its preceding projection.
"""

import pytest

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.portfolio.household_example import synthetic


@pytest.mark.parametrize(
    "field",
    [
        "complete_ownership_and_outside_purchases_confirmed",
        "monthly_settlement_and_cash_sweep_confirmed",
    ],
)
def test_linked_lot_confirmations_are_required(field):
    data = synthetic().model_dump(mode="json")
    data["lot_plan"][field] = False
    with pytest.raises(ValueError, match="Confirm complete lot"):
        project(Scenario.model_validate(data))


def test_opening_balance_must_be_the_same_linked_capital():
    data = synthetic().model_dump(mode="json")
    data["accounts"][-1]["balance"] = "100001"
    with pytest.raises(ValueError, match="opening balance"):
        project(Scenario.model_validate(data))


def test_old_proportional_seller_cannot_sell_the_same_linked_account():
    data = synthetic().model_dump(mode="json")
    data["tax_plan"]["funding_sources"] = [
        dict(
            account_id="brokerage",
            federal_basis="58000",
            nj_basis="54000",
            federal_character="long_term",
            loss_treatment="allowed",
            liquid_after="2020-01-01",
        )
    ]
    with pytest.raises(ValueError, match="proportional-basis seller"):
        project(Scenario.model_validate(data))


def test_missing_monthly_mark_cannot_use_a_later_price():
    data = synthetic().model_dump(mode="json")
    data["lot_plan"]["monthly_marks"].pop(3)
    with pytest.raises(ValueError, match="every household month"):
        project(Scenario.model_validate(data))


def test_linked_owner_must_match_the_actual_filing_person():
    data = synthetic().model_dump(mode="json")
    data["lot_plan"]["case"]["accounts"][0]["owner"] = "spouse"
    with pytest.raises(ValueError, match="owner, USD taxable"):
        project(Scenario.model_validate(data))


def test_lot_projection_preserves_immutable_inputs_and_json_roundtrip():
    case = synthetic()
    before = case.model_dump_json()
    rows = project(case)
    assert case.model_dump_json() == before
    assert project(Scenario.model_validate_json(before)) == rows
