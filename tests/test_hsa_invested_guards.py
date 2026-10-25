"""Reject duplicate assets, tax recognition and ambiguous cash-only declarations."""

import pytest

from wealthlab.household.scenario import Scenario
from wealthlab.retirement.hsa_household_validation import validate
from wealthlab.retirement.hsa_invested_example import synthetic


@pytest.mark.parametrize(
    "flag",
    [
        "cash_accounts_outside_investment_book_confirmed",
        "investment_income_excluded_from_other_inputs_confirmed",
    ],
)
def test_missing_confirmation_blocks_invested_household(flag):
    data = synthetic().model_dump(mode="json")
    data["hsa_plan"][flag] = False
    with pytest.raises(ValueError, match="Confirm remaining cash HSAs"):
        validate(Scenario.model_validate(data))


def test_cash_only_declaration_cannot_contradict_positions():
    data = synthetic().model_dump(mode="json")
    data["hsa_plan"]["cash_only_accounts_and_complete_context_confirmed"] = True
    with pytest.raises(ValueError, match="cash-only household"):
        validate(Scenario.model_validate(data))


def test_opening_position_value_cannot_disagree_with_household_balance():
    data = synthetic().model_dump(mode="json")
    data["accounts"][1]["balance"] = 10000
    with pytest.raises(ValueError, match="opening value"):
        validate(Scenario.model_validate(data))


def test_recipient_fraction_cannot_retax_already_recognized_state_investment_income():
    data = synthetic().model_dump(mode="json")
    data["hsa_plan"]["nj_withdrawal_taxable_fractions"] = dict(care=".1")
    data["hsa_plan"]["generated_distribution_tax_excluded_from_other_inputs_confirmed"] = True
    with pytest.raises(ValueError, match="zero recipient taxable fractions"):
        validate(Scenario.model_validate(data))
