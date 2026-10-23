"""IRS Schedule D worksheet cases independently calculated from character nets."""

from decimal import Decimal

import pytest

from wealthlab.tax.capital import next_carry


@pytest.mark.parametrize(
    ("st", "lt", "taxable", "deduction", "expected"),
    [
        (-10000, 0, 100000, 3000, (7000, 0)),
        (-10000, 0, -34500, 3000, (10000, 0)),
        (-10000, 0, -1500, 3000, (8500, 0)),
        (-2000, -10000, 100000, 3000, (0, 9000)),
        (-10000, 4000, 100000, 3000, (3000, 0)),
        (4000, -10000, 100000, 3000, (0, 3000)),
    ],
)
def test_character_carry(st, lt, taxable, deduction, expected):
    result = next_carry(Decimal(st), Decimal(lt), Decimal(taxable), Decimal(deduction))
    assert (result["short_term"], result["long_term"]) == expected
