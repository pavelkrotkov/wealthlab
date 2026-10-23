"""Tacking adds actual ownership periods, not the gap before a later replacement."""

import pytest
from test_wash_sales import wash_case

from wealthlab.portfolio.cases import LotCase
from wealthlab.portfolio.engine import run


@pytest.mark.parametrize(
    "exit_date,character",
    [
        ("2026-06-02", "short_term"),
        ("2026-06-21", "short_term"),
        ("2026-06-22", "long_term"),
    ],
)
def test_post_sale_gap_is_not_counted_as_ownership(exit_date, character):
    # June 1, 2025 -> May 1, 2026: 334 days. Buy again May 21.
    # On June 2 the second period is 12 days, so total holding is only 346 days.
    # Returning the original acquisition date would incorrectly label that LT.
    # The equivalent holding start is June 21, 2025: June 21 is exactly one
    # year, and June 22 exceeds one year. Pub 550 says to add periods held.
    payload = wash_case().model_dump(mode="json")
    payload["lots"][0].update(acquired="2025-06-01", federal_holding_start="2025-06-01")
    payload["trades"][0]["date"] = "2026-05-01"
    payload["trades"][1]["date"] = "2026-05-21"
    payload["trades"].append(
        dict(payload["trades"][1], id="exit", action="sell", date=exit_date, price="12")
    )
    result = run(LotCase.model_validate(payload))
    last = result["disposals"][-1]
    assert last["federal_holding_start"] == "2025-06-21"
    assert last["federal_character"] == character
