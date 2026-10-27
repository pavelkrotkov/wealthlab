"""A frozen future-year illustration and a supplied treaty claim need explicit profiles."""

from wealthlab.tax.spain import evaluate
from wealthlab.tax.spain_example import synthetic
from wealthlab.tax.spain_inputs import SpainCase


def test_future_year_reuses_schedules_only_when_explicitly_labelled_frozen():
    data = synthetic().model_dump(mode="json")
    data.update(year=2026, as_of="2027-07-31", policy="frozen_2025")
    for item in data["incomes"]:
        item["amount"]["date"] = "2026-12-31"
    for asset in data["assets"]:
        asset["fiscal_value"]["date"] = "2026-12-31"
    result = evaluate(SpainCase.model_validate(data))
    assert result["income"]["assessment"]["liability"] == 12787
    assert "frozen_2025" in result["policy"]
    assert result["liability_year"] == 2026


def test_unknown_citizenship_cannot_qualify_a_supplied_treaty_exemption():
    data = synthetic().model_dump(mode="json")
    data["citizenship"] = "unknown"
    data["incomes"][0].update(spanish_base="exempt", treaty_treatment="supplied_exemption")
    result = evaluate(SpainCase.model_validate(data))
    assert result["income"]["assessment"] is None
    assert "citizenship" in result["income"]["reasons"][0]
