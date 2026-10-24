"""Trade chronology, liquidity and calendar holding periods are explicit constraints."""

from datetime import date

import pytest

from wealthlab.portfolio.cases import LotCase
from wealthlab.portfolio.disposal import is_long
from wealthlab.portfolio.engine import run
from wealthlab.portfolio.example import synthetic


@pytest.mark.parametrize(("sold", "expected"), [("2025-02-28", False), ("2025-03-01", True)])
def test_leap_day_holding_period(sold, expected):
    assert is_long(date(2024, 2, 29), date.fromisoformat(sold)) is expected


def test_locked_specific_lot_is_not_sold():
    payload = synthetic().model_dump(mode="json")
    payload["lots"][0]["liquid_after"] = "2027-01-01"
    payload["trades"][0].update(selection="specific", lot_ids=["original"])
    with pytest.raises(ValueError, match="liquid"):
        run(LotCase.model_validate(payload))


@pytest.mark.parametrize(("field", "value"), [("date", "2027-01-01"), ("account_id", "absent")])
def test_bad_dates_and_references_block(field, value):
    payload = synthetic().model_dump(mode="json")
    payload["trades"][0][field] = value
    with pytest.raises(ValueError):
        run(LotCase.model_validate(payload))
