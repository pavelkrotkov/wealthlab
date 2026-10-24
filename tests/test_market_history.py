"""Historical replay preserves sequence, asset identity and supplied provenance."""

import pytest

from wealthlab.markets.example import synthetic
from wealthlab.markets.inputs import MarketCase
from wealthlab.markets.paths import generate


def test_invented_history_maps_by_asset_identity_without_reordering_months():
    case = synthetic("historical")
    batch = generate(case)
    assert batch.mark_returns[0, 3, 2] == case.historical.months[3].mark_returns["employer"]
    assert batch.cash_yields[0, 3, 1] == 0.03 / 12
    assert batch.dates[0].isoformat() == "2027-01-01"
    assert batch.metadata["historical_synthetic"] is True
    assert "Invented" in batch.metadata["input"]["historical"]["source"]


@pytest.mark.parametrize("change", ["gap", "day", "duplicate", "missing_asset", "unavailable"])
def test_incomplete_or_unavailable_history_is_rejected(change):
    data = synthetic("historical").model_dump(mode="json")
    mutate(data, change)
    with pytest.raises(ValueError):
        MarketCase.model_validate(data)


def mutate(data, change):
    history = data["historical"]
    edits = {
        "gap": lambda: history["months"].pop(2),
        "day": lambda: history["months"][0].update(date="2000-01-02"),
        "duplicate": lambda: history["months"][1].update(date="2000-01-01"),
        "missing_asset": lambda: history["months"][0]["mark_returns"].pop("employer"),
        "unavailable": lambda: history.update(available_as_of="2028-01-01"),
    }
    edits[change]()


def test_partial_last_month_is_not_complete_historical_coverage():
    data = synthetic("historical").model_dump(mode="json")
    data["historical"].update(available_as_of="2009-12-15")
    with pytest.raises(ValueError, match="complete and available"):
        MarketCase.model_validate(data)


def test_total_return_history_cannot_hide_cash_distributions_in_observations():
    data = synthetic("historical").model_dump(mode="json")
    data["return_convention"] = "total_return_reinvested"
    for asset in data["assets"]:
        asset["annual_cash_yield"] = 0
    with pytest.raises(ValueError, match="cannot also pay cash"):
        MarketCase.model_validate(data)
