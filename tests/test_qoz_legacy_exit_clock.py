"""Legacy designation-expiry continuation cannot be assumed beyond the2047 safe harbor.

The existing regulation1.1400Z2(c)-1(c) limits its continuation rule. It does
not prove that every later legacy election is legally denied, so this profile
fails closed instead of silently granting or categorically denying the benefit.
"""

from datetime import date
from decimal import Decimal
from types import SimpleNamespace

import pytest

from wealthlab.products.qoz_exit import exit_event
from wealthlab.products.qoz_tax import include, inclusion_date, opening


@pytest.mark.parametrize(
    "invested,sold,unsupported",
    [
        (date(2026, 1, 31), date(2047, 12, 31), False),
        (date(2026, 1, 31), date(2048, 1, 31), True),
        (date(2027, 1, 31), date(2048, 1, 31), False),
    ],
)
def test_legacy_and_post_2026_exit_clocks_remain_distinct(invested, sold, unsupported):
    plan = SimpleNamespace(
        federal="allowed", new_jersey="deferred", rural_30_percent_assumed_confirmed=False
    )
    tax = opening(
        Decimal(100000),
        dict(federal=Decimal(100000), new_jersey=Decimal(100000)),
        invested,
        "long_term",
    )
    include(tax, Decimal(100000), inclusion_date(invested), plan)
    if unsupported:
        with pytest.raises(ValueError, match="post-2047"):
            exit_event(tax, Decimal(150000), Decimal(150000), sold, plan)
    else:
        result = exit_event(tax, Decimal(150000), Decimal(150000), sold, plan)
        assert result.federal.long_term == 0
