"""Reject unsupported fund-loss treatment and prevent total-return double counting."""

import pytest
from distribution_cases import distribution_case, trade

from wealthlab.portfolio.cases import LotCase
from wealthlab.portfolio.engine import run


def test_distributions_require_price_only_confirmation():
    payload = distribution_case()
    payload["price_only_marks_confirmed"] = False
    with pytest.raises(ValueError, match="total-return"):
        run(LotCase.model_validate(payload))


def test_capital_distribution_short_fund_loss_is_not_silently_ordinary():
    payload = distribution_case()
    payload["as_of"] = "2026-05-01"
    payload["lots"][0].update(acquired="2026-05-01", federal_holding_start="2026-05-01")
    payload["securities"][0]["kind"] = "etf"
    payload["distributions"][0].update(federal_character="long_term", qualified_fraction="0")
    payload["trades"] = [trade("sell", "2026-06-10", price="5")]
    with pytest.raises(ValueError, match="special loss adjustments"):
        run(LotCase.model_validate(payload))
    # A later distribution on shares no longer owned cannot trigger the guard.
    payload["distributions"][0].update(
        ex_date="2026-07-01", payment_date="2026-07-15", recognition_date="2026-07-15"
    )
    result = run(LotCase.model_validate(payload))
    assert not result["distributions"]
    assert result["disposals"][0]["federal_recognized_gain"] == -500


@pytest.mark.parametrize(
    "federal,nj",
    [
        ("interest", "interest"),
        ("tax_exempt_interest", "interest"),
        ("long_term", "dispositions"),
    ],
)
def test_independent_jurisdiction_characters_reach_the_annual_engine(federal, nj):
    payload = distribution_case()
    payload["distributions"][0].update(
        federal_character=federal, nj_character=nj, qualified_fraction="0"
    )
    row = run(LotCase.model_validate(payload))["annual_tax_comparison"][0]
    assert row["distribution_federal"][federal] == 100
    assert row["distribution_nj"][nj] == 100
    assert row["with_lot_trades"]["total_liability"] > row["without_lot_trades"]["total_liability"]
