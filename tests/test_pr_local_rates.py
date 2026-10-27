"""Independent published schedule boundaries, flat ABT bands and explicit statutory cap."""

from decimal import Decimal

import pytest

from wealthlab.tax.pr_local_rates import abt, bracket, gradual, regular


@pytest.mark.parametrize(
    "income,expected",
    [(9000, "0"), (25000, "1120"), (41500, "3430"), (61500, "8430"), (96500, "19980")],
)
def test_regular_table_uses_published_breakpoints(income, expected):
    assert bracket(Decimal(income)) == Decimal(expected)


def test_hundred_thousand_reduction_boundary_uses_gross_income():
    assert regular(Decimal(96500), Decimal(3500), Decimal(100000))["tax"] == Decimal("18381.60")
    assert regular(Decimal(96501), Decimal(3500), Decimal(100001))["tax"] == Decimal("18981.31")


def test_gradual_adjustment_uses_published_cap_and_personal_exemption():
    assert gradual(Decimal(500000), Decimal(3500)) == 0
    assert gradual(Decimal(500100), Decimal(3500)) == 5
    assert gradual(Decimal(1000000), Decimal(3500)) == 10050
    assert regular(Decimal(1000000), Decimal(3500), Decimal(1003500))["tax"] == Decimal("311775.75")


@pytest.mark.parametrize(
    "income,expected",
    [
        (25000, "0"),
        (50000, "500"),
        (50001, "1500.03"),
        (75001, "3750.05"),
        (150001, "15000.10"),
        (250001, "60000.24"),
    ],
)
def test_abt_is_the_published_flat_band_rate(income, expected):
    assert abt(Decimal(income)) == Decimal(expected)


def test_wage_only_profile_is_not_subject_to_abt():
    assert abt(Decimal(1000000), wage_only=True) == 0
