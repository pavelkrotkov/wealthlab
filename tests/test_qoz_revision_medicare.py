"""Corrected MAGI reaches actual future premiums while historical bills remain fixed.

The source-year salary is $180,000. The stock sale adds $80,000 federal gain,
raising uncorrected MAGI to $260,000; the actual later QOZ election returns it
to $180,000. Under the explicit frozen premium schedule these straddle a tier.
"""

import pytest
from qoz_medicare_cases import case

from wealthlab.household.projection import project


@pytest.fixture(scope="module")
def bills():
    scenario = case()
    denied = scenario.model_copy(
        update=dict(
            qoz_plan=scenario.qoz_plan.model_copy(
                update=dict(federal="denied", new_jersey="denied")
            )
        )
    )
    return {
        "allowed": project(scenario)[-1]["medicare_audit"]["bills"],
        "denied": project(denied)[-1]["medicare_audit"]["bills"],
    }


def test_original_source_year_magi_is_replaced_in_the_future_lookback(bills):
    allowed = [b for b in bills["allowed"] if b["date"].year == 2028]
    denied = [b for b in bills["denied"] if b["date"].year == 2028]
    assert allowed
    assert all(b["income_year"] == 2026 and b["magi"] == 180000 and b["tier"] == 0 for b in allowed)
    assert all(b["magi"] == 260000 and b["tier"] == 1 for b in denied)


def test_revision_does_not_rewrite_already_billed_source_year_premiums(bills):
    allowed = [b for b in bills["allowed"] if b["date"].year == 2026]
    denied = [b for b in bills["denied"] if b["date"].year == 2026]
    assert allowed == denied
