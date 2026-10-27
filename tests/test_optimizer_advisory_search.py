"""The search ranks actual after-fee outcomes and freezes its held-out contract.

Each option unit earns $496 and the new policy earns $100 before the common
terminal-year invoice. The native fee consumes one percent of current assets;
no candidate can exchange that shared contract for a zero-cost assumption.
"""

from decimal import Decimal

import pytest

from tests.optimizer_advisory_cases import case
from wealthlab.optimization.search import search


@pytest.fixture(scope="module")
def result():
    return search(case())


def test_search_selects_actual_native_units_under_the_common_fee_contract(result):
    assert result["evaluated_candidates"] == 6
    assert result["configured_validation_passed"] is True
    winner = next(c for c in result["candidates"] if c["candidate"] == result["selection"])
    assert winner["choices"]["new_option_purchase"] == "two"
    assert winner["choices"]["new_policy_purchase"] == "supplied_policy"


def test_actual_after_fee_winner_and_heldout_wealth_reconcile(result):
    winner = next(c for c in result["candidates"] if c["candidate"] == result["selection"])
    assert winner["median_real_after_tax_exit_wealth"] == Decimal("250540.09")
    assert winner["median_advisory_fees_paid"] == Decimal("2550.91")
    assert result["held_out"]["assessment"]["median_real_after_tax_exit_wealth"] == Decimal(
        "250540.09"
    )


def test_training_and_validation_export_the_identical_common_fee_contract_and_actual_debt(result):
    model = case()
    common = model.household.advisory_fee_plan.model_dump(mode="json")
    training = result["selected_training"]
    heldout = result["held_out"]["results"]
    assert (
        training["household"]["advisory_fee_plan"]
        == heldout["household"]["advisory_fee_plan"]
        == common
    )
    final = heldout["details"][0]["rows"][-1]
    assert final["advisory_fee_audit"]["inputs"] == common
    assert final["advisory_fees_owed"] == final["fees_owed"] == 0
    assert final["advisory_fee_audit"]["assessments"][0]["valuation_base"] == 255091
