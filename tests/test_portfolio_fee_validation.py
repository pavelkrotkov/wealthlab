"""Contract assumptions and valuation timestamps must be explicit before assessment."""

import pytest
from fee_cases import fee_case

from wealthlab.portfolio.cases import LotCase
from wealthlab.portfolio.engine import run


@pytest.mark.parametrize(
    "changes",
    [
        dict(provenance="unresolved"),
        dict(account_ids=["missing"]),
        dict(security_ids=["missing"]),
        dict(account_ids=["brokerage", "brokerage"]),
        dict(payment_account="missing"),
    ],
)
def test_ambiguous_fee_scope_is_rejected(changes):
    payload = fee_case()
    payload["fee_schedules"][0].update(changes)
    with pytest.raises(ValueError):
        run(LotCase.model_validate(payload))


def test_overlapping_periods_and_missing_snapshot_are_rejected():
    payload = fee_case()
    period = payload["fee_schedules"][0]["periods"][0]
    payload["fee_schedules"][0]["periods"].append(dict(period, date="2026-01-12"))
    with pytest.raises(ValueError, match="overlap"):
        run(LotCase.model_validate(payload))
    payload["fee_schedules"][0]["periods"].pop()
    period["prices"].pop("ETF")
    with pytest.raises(ValueError, match="snapshot"):
        run(LotCase.model_validate(payload))


def test_supplied_contract_base_is_separate_from_marked_portfolio_value():
    payload = fee_case()
    payload["fee_schedules"][0]["periods"][0]["supplied_base"] = "5000"
    result = run(LotCase.model_validate(payload))
    assert result["fee_assessments"][0]["base_source"] == "supplied"
    assert result["fee_summary"]["cash_assessed"] == 55
    assert result["gross_wealth"] == 1945
