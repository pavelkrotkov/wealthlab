"""Spouses can allocate their shared base but cannot transfer an owner's catch-up."""

import pytest
from test_hsa_cash import calculate, payload


def family_case():
    data = payload()
    data.update(contributions=[], withdrawals=[], interest=[])
    for owner in data["owners"]:
        for month in owner["months"]:
            month["medicare"] = False
    return data


def test_both_eligible_spouses_share_base_and_keep_own_catchup():
    data = family_case()
    for month in data["owners"][0]["months"]:
        month["family_share"] = "1"
    for month in data["owners"][1]["months"]:
        month["family_share"] = "0"
    assert calculate(data)["contribution_limits"] == {"person": 9750, "spouse": 1000}


def test_default_family_split_is_equal_when_both_are_eligible():
    assert calculate(family_case())["contribution_limits"] == {"person": 5375, "spouse": 5375}


def test_overlapping_family_allocations_are_rejected():
    data = family_case()
    for owner in data["owners"]:
        for month in owner["months"]:
            month["family_share"] = ".6"
    with pytest.raises(ValueError, match="shared monthly"):
        calculate(data)
