"""Unfunded entries, explicit loan interest and unmatched tax instructions stay visible."""

from decimal import Decimal

import pytest

from tests.option_cases import one_leg, parse
from wealthlab.products.option_engine import run


def test_explicit_settlement_loan_survives_and_pays_actual_supplied_interest():
    data = one_leg(physical=True)
    data["holdings"].update(end="2026-02-01")
    data["holdings"]["accounts"][0]["cash"] = "500"
    data.update(outside_cash="0", allow_settlement_loan=True)
    data["marks"].append(dict(data["marks"][-1], date="2026-02-01"))
    result = run(parse(data))
    assert result["ending"]["loan"] == Decimal("10050.96")
    assert result["ending"]["wealth"] == Decimal("13949.04")
    assert result["cash_movements"][-1]["amount"] == Decimal("-50.96")


def test_unfunded_option_premium_does_not_create_a_position_or_free_credit():
    data = one_leg()
    data["holdings"]["accounts"][0]["cash"] = "0"
    data["outside_cash"] = "0"
    result = run(parse(data))
    assert result["ending"]["cash"] == 0
    assert not result["terminations"]
    assert "unfunded opening premium" in result["failures"][0]


@pytest.mark.parametrize(
    "key,profile,message",
    [
        ("contract:2026-01-02", "supplied_deferrals", "unmatched recognition ID"),
        ("contract:2026-01-01", "assume_not_applicable", "supplied_deferrals profile"),
    ],
)
def test_supplied_tax_deferral_cannot_be_ignored_or_conflict_with_profile(key, profile, message):
    data = one_leg()
    data["marks"][-1]["stock"] = "80"
    data["tax"].update(straddle=profile, federal_deferrals={key: "300"})
    with pytest.raises(ValueError, match=message):
        run(parse(data))
