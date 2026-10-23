"""The 30-day window is inclusive, while a closing-date observation includes that day's trades."""

from decimal import Decimal as D

import pytest
from test_wash_sales import wash_case

from wealthlab.portfolio.cases import LotCase
from wealthlab.portfolio.engine import run


@pytest.mark.parametrize(("purchase", "disallowed"), [("2026-07-01", 250), ("2026-07-02", 0)])
def test_post_sale_boundary(purchase, disallowed):
    payload = wash_case().model_dump(mode="json")
    payload["trades"][1]["date"] = purchase
    row = run(LotCase.model_validate(payload))["disposals"][0]
    assert row["federal_wash_disallowed"] == disallowed
    assert row["federal_recognized_gain"] == -250 + disallowed


@pytest.mark.parametrize(("end", "pending"), [("2026-06-30", 250), ("2026-07-01", 0)])
def test_unmatched_window_closes_at_end_of_day_30(end, pending):
    payload = wash_case().model_dump(mode="json")
    payload.update(end=end, trades=payload["trades"][:1])
    row = run(LotCase.model_validate(payload))["disposals"][0]
    assert row["federal_pending_loss"] == pending
    assert row["federal_recognized_gain"] == -250 + pending


def test_gain_does_not_create_a_wash_loss():
    payload = wash_case().model_dump(mode="json")
    payload["trades"][0]["price"] = "12"
    result = run(LotCase.model_validate(payload))
    assert result["disposals"][0]["federal_recognized_gain"] == 200
    assert result["disposals"][0]["federal_wash_disallowed"] == 0
    assert D(result["lots"][0]["federal_basis"]) == 800


def test_unconfirmed_opening_wash_history_blocks_tracking():
    case = wash_case().model_copy(update={"opening_wash_context_complete": False})
    with pytest.raises(ValueError, match="complete opening household context"):
        run(case)
