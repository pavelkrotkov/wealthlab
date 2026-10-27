"""Each spouse retains residence, NJ source and January-age exemption facts.

The state exception splits NJ returns without changing the federal joint unit.
An older full-nonresident spouse receives that spouse's own exemption, while
both spouses with common residence periods may use the joint schedule.
"""

from copy import deepcopy

import pytest
from nj_residence_helpers import edited, results

from wealthlab.tax.nj_residence_example import row


def mixed(profile, data):
    other = deepcopy(profile["people"][0])
    other.update(id="person_b", role="spouse", status="nonresident", periods=[])
    profile["people"].append(other)
    profile["filing_election"] = "mixed_spouse_separate"
    profile["income"].append(
        row("spouse_nj_work", "2025-09-30", 20000, "allowed", owner="person_b")
    )
    data["filing"].update(status="joint", age_spouse=67)
    data["nj_income"]["wages"] = "120000"


def test_full_nonresident_spouse_and_part_resident_spouse_use_supported_separate_exception():
    rows = results(edited(mixed))
    assert [r["owners"] for r in rows] == [["person_a"], ["person_a"], ["person_b"]]
    assert {r["filing_status"] for r in rows} == {"separate"}
    assert rows[-1]["prorated_exemptions"] == 2000
    assert rows[-1]["income_tax"] == 252


def test_common_spouse_periods_can_follow_federal_joint_filing():
    def change(profile, data):
        mixed(profile, data)
        profile["filing_election"] = "follow_federal"
        profile["people"][1].update(
            status="part_year", periods=deepcopy(profile["people"][0]["periods"])
        )

    rows = results(edited(change))
    assert len(rows) == 2
    assert {r["filing_status"] for r in rows} == {"joint"}
    assert rows[0]["prorated_exemptions"] == 1500


def test_different_spouse_periods_do_not_silently_elect_joint_worldwide_residence():
    def change(profile, data):
        mixed(profile, data)
        profile["filing_election"] = "follow_federal"

    with pytest.raises(ValueError, match="Different spouse"):
        results(edited(change))


def test_both_full_nonresident_with_only_one_nj_source_spouse_can_file_that_spouse_separately():
    def change(profile, data):
        mixed(profile, data)
        profile["people"][0].update(status="nonresident", periods=[])
        profile["filing_election"] = "one_nonresident_source_separate"
        for item in profile["income"]:
            if item["owner_id"] == "person_a":
                item["nj_source"] = "denied"

    rows = results(edited(change))
    assert rows[0]["income_tax"] == 0
    assert rows[1]["income_tax"] == 252
