"""Exact fractions prevent one-dime errors at statutory reduction boundaries."""

from datetime import date
from decimal import Decimal

import pytest

from wealthlab.retirement.social_amounts import pia, reduced
from wealthlab.retirement.social_example import synthetic


@pytest.mark.parametrize(
    ("amount", "months", "spouse", "expected"),
    [
        ("980.50", 44, False, "751.70"),
        ("1000", 60, False, "700"),
        ("1440", 1, False, "1432"),
        ("1440", 1, True, "1430"),
        ("250", 60, True, "162.50"),
        ("1000.90", 0, False, "1000.90"),
    ],
)
def test_primary_source_reductions_and_exact_dime_boundaries(amount, months, spouse, expected):
    assert reduced(Decimal(amount), months, spouse) == Decimal(expected)


def test_cola_truncates_each_year_and_starts_with_december_entitlement():
    person = synthetic().members[1].model_copy(update={"pia_january_2026": Decimal("1000.10")})
    assert pia(person, date(2026, 11, 1), Decimal("0.033")) == Decimal("1000.10")
    assert pia(person, date(2026, 12, 1), Decimal("0.033")) == Decimal("1033.10")
    assert pia(person, date(2027, 12, 1), Decimal("0.033")) == Decimal("1067.10")

    assert pia(person, date(2028, 12, 1), Decimal("0.033")) == Decimal("1102.30")
