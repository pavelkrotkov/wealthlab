"""Locked/zero strategies cannot hide missing fee scope or an unsupported future-account basis."""

import pytest

from tests.optimizer_advisory_cases import case
from wealthlab.optimization.inputs import PolicySearch
from wealthlab.optimization.validation import validate


def test_missing_optional_account_coverage_rejects_even_a_locked_zero_purchase():
    data = case().model_dump(mode="json")
    data["dimensions"][1]["locked_choice"] = "cash"
    covered = data["household"]["advisory_fee_plan"]["schedules"][0]["covered"]
    account = data["option_opportunity"]["unit"]["account_id"]
    data["household"]["advisory_fee_plan"]["schedules"][0]["covered"] = [
        r for r in covered if r["account_id"] != account
    ]
    with pytest.raises(ValueError, match="explicitly name every strategy"):
        validate(PolicySearch.model_validate(data))


def test_inactive_life_offer_requires_explicit_native_life_basis_in_common_contract():
    data = case().model_dump(mode="json")
    data["dimensions"][2]["locked_choice"] = "no_new_policy"
    account = data["new_life_opportunities"][0]["holding"]["account_id"]
    covered = data["household"]["advisory_fee_plan"]["schedules"][0]["covered"]
    next(r for r in covered if r["account_id"] == account)["value_basis"] = (
        "modeled_net_account_equity"
    )
    with pytest.raises(ValueError, match="supported native value basis"):
        validate(PolicySearch.model_validate(data))


def test_missing_if_present_source_confirmation_is_not_a_free_absent_account():
    data = case().model_dump(mode="json")
    row = data["household"]["advisory_fee_plan"]["schedules"][0]["covered"][-1]
    row["absence_permitted_by_source_confirmed"] = False
    with pytest.raises(ValueError, match="source-confirmed absence"):
        validate(PolicySearch.model_validate(data))
