"""Incomplete terms cannot silently turn an illustration into a safe household plan."""

import pytest

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.products.life_household_example import synthetic


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("payments_complete_through", "2026-04-01", "reserve horizon"),
        ("other_inputs_exclude_policy_confirmed", False, "duplicated cash"),
        ("failure_exits", {}, "failure exit"),
    ],
)
def test_incomplete_payment_obligations_cannot_claim_household_success(field, value, message):
    data = synthetic().model_dump(mode="json")
    data["life_plan"]["holdings"][0][field] = value
    with pytest.raises(ValueError, match=message):
        project(Scenario.model_validate(data))


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("federal_status", "unknown", "eligibility"),
        ("values_match_executed_events_confirmed", False, "executed path"),
        ("values", [], "month end"),
        ("opening_loan", "100", "less loan debt"),
    ],
)
def test_unresolved_policy_assets_or_taxes_are_rejected(field, value, message):
    data = synthetic().model_dump(mode="json")
    data["life_plan"]["holdings"][0]["contract"][field] = value
    with pytest.raises(ValueError, match=message):
        project(Scenario.model_validate(data))


def test_an_insurance_account_cannot_remain_unowned_after_disabling_the_policy():
    data = synthetic().model_dump(mode="json")
    data["life_plan"] = None
    with pytest.raises(ValueError, match="Every insurance account"):
        Scenario.model_validate(data)
