"""Published regional quotas and AEAT's 2025 Toledo income numbers are independent oracles."""

from decimal import Decimal

import pytest

from wealthlab.tax.spain import evaluate
from wealthlab.tax.spain_example import income, synthetic
from wealthlab.tax.spain_inputs import SpainCase
from wealthlab.tax.spain_rates import CATALONIA, MADRID, SAVINGS, scale


def test_official_toledo_general_and_savings_quotas():
    result = evaluate(synthetic())["income"]["assessment"]
    assert result["liquidable_general"] == 48000
    assert result["state"]["general"] + result["regional"]["general"] == 12407
    assert result["state"]["savings"] + result["regional"]["savings"] == 380
    assert result["liability"] == 12787


@pytest.mark.parametrize(
    "base,quota",
    [
        ("13362.22", "1135.79"),
        ("19004.63", "1739.53"),
        ("35425.68", "3841.42"),
        ("57320.40", "7651.10"),
    ],
)
def test_published_madrid_boundary(base, quota):
    assert scale(Decimal(base), MADRID) == Decimal(quota)


@pytest.mark.parametrize(
    "base,quota",
    [
        (12500, "1187.50"),
        (22000, "2375"),
        (33000, "4135"),
        (53000, "7935"),
        (90000, "15890"),
        (120000, "22940"),
        (175000, "36415"),
    ],
)
def test_published_catalonia_boundary(base, quota):
    assert scale(Decimal(base), CATALONIA) == Decimal(quota)


def test_savings_2025_top_combined_rate_is_thirty_percent():
    assert scale(Decimal(310000), SAVINGS) * 2 == 74880
    assert scale(Decimal(310100), SAVINGS) * 2 == 74910


def test_unused_personal_minimum_reduces_savings_quota_through_the_schedule():
    data = synthetic().model_dump(mode="json")
    data.update(
        incomes=[income("saving", 8000, "savings")],
        general_reduction_eur="0",
        long_held_gain_cap_exclusion_eur="0",
    )
    result = evaluate(SpainCase.model_validate(data))["income"]["assessment"]
    assert result["liability"] == Decimal("505.50")
    assert result["state"]["general"] == 0
