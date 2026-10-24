"""Official CMS boundaries distinguish inclusive intermediate limits from inclusive top tiers."""

from decimal import Decimal

import pytest

from wealthlab.retirement.medicare_example import synthetic
from wealthlab.retirement.medicare_rules import tier


@pytest.mark.parametrize(
    ("filing", "magi", "expected"),
    [
        ("individual", "109000", 0),
        ("individual", "109000.01", 1),
        ("individual", "137000", 1),
        ("individual", "137000.01", 2),
        ("individual", "171000", 2),
        ("individual", "171000.01", 3),
        ("individual", "205000", 3),
        ("individual", "205000.01", 4),
        ("individual", "499999.99", 4),
        ("individual", "500000", 5),
        ("joint", "218000", 0),
        ("joint", "274000", 1),
        ("joint", "342000", 2),
        ("joint", "410000", 3),
        ("joint", "410000.01", 4),
        ("joint", "750000", 5),
        ("separate_lived_together", "109000", 0),
        ("separate_lived_together", "109000.01", 4),
        ("separate_lived_together", "390999.99", 4),
        ("separate_lived_together", "391000", 5),
        ("separate_lived_apart", "137000", 1),
        ("individual", "-1000", 0),
    ],
)
def test_published_2026_thresholds(filing, magi, expected):
    assert tier(synthetic(), 2026, filing, Decimal(magi)) == expected
