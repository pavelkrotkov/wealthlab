"""Tax benefit is a matched filing-unit liability difference, not a loss times a rate."""

import pytest
from test_nj_wash import nj_case

from wealthlab.portfolio.cases import LotCase
from wealthlab.portfolio.engine import run
from wealthlab.tax.annual import synthetic


def forecast(year=2026):
    result = synthetic().model_dump(mode="json")
    result["policy"].update(year=year, mode="freeze_2025")
    result["nj_regime"] = "freeze_2025"
    return result


def reporting_case(**kwargs):
    payload = nj_case(**kwargs)
    payload["lot_tax_cases"] = [forecast()]
    return payload


def test_recognized_loss_offsets_federal_wages_but_not_nj_wages():
    payload = reporting_case()
    payload["trades"] = payload["trades"][:1]
    row = run(LotCase.model_validate(payload))["annual_tax_comparison"][0]
    assert row["recognized_federal"]["long_term"] == -250
    assert row["recognized_nj"] == -250
    assert row["incremental_liability"] == -55
    assert row["with_lot_trades"]["new_jersey"] == row["without_lot_trades"]["new_jersey"]


def test_deferred_loss_has_no_immediate_liability_benefit():
    row = run(LotCase.model_validate(reporting_case()))["annual_tax_comparison"][0]
    assert row["incremental_liability"] == 0
    assert row["recognized_federal"]["long_term"] == 0
    assert row["recognized_nj"] == 0


def test_each_scenario_propagates_its_own_carry_and_nj_has_no_capital_carry():
    """A 10,000 loss consumes 3,000 in year one and leaves 7,000 federal carry.

    In year two it offsets an external 5,000 gain plus 2,000 ordinary income;
    NJ cannot reuse the prior-year loss against that second-year gain.
    """
    payload = reporting_case(end="2027-12-31")
    payload["trades"] = payload["trades"][:1]
    payload["lots"][0].update(federal_basis="10750", nj_basis="10750")
    later = forecast(2027)
    later["federal_income"]["long_term"] = "5000"
    later["nj_income"]["dispositions"] = "5000"
    payload["lot_tax_cases"].append(later)
    first, second = run(LotCase.model_validate(payload))["annual_tax_comparison"]
    assert first["with_lot_trades"]["federal"]["long_carry"] == 7000
    assert first["without_lot_trades"]["federal"]["long_carry"] == 0
    assert second["with_lot_trades"]["federal"]["long_carry"] == 0
    assert second["incremental_liability"] == -1190
    assert second["with_lot_trades"]["new_jersey"] == second["without_lot_trades"]["new_jersey"]


@pytest.mark.parametrize(
    "change, message",
    [
        ({"nj_wash_treatment": "unconfirmed"}, "explicit NJ"),
        ({"federal_wash_tracking": False}, "federal wash"),
        ({"end": "2027-12-31"}, "every projection"),
    ],
)
def test_missing_recognition_or_forecast_blocks_tax_claim(change, message):
    payload = dict(reporting_case(), **change)
    with pytest.raises(ValueError, match=message):
        run(LotCase.model_validate(payload))


def test_later_carry_cannot_be_entered_and_computed_twice():
    payload = reporting_case(end="2027-12-31")
    later = forecast(2027)
    later["federal_income"]["long_carry"] = "10"
    payload["lot_tax_cases"].append(later)
    with pytest.raises(ValueError, match="only in the first year"):
        run(LotCase.model_validate(payload))
