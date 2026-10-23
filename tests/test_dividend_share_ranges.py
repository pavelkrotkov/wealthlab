"""Qualification must follow the particular shares entitled to the dividend."""

from distribution_cases import distribution_case, trade
from test_dividend_qualification import recently_acquired

from wealthlab.portfolio.cases import LotCase
from wealthlab.portfolio.engine import run


def test_sixty_days_fails_but_sixty_one_days_qualifies():
    payload = recently_acquired()
    payload["trades"] += [
        trade("sell", "2026-07-14", qty="50", id="day60"),
        trade("sell", "2026-07-15", qty="50", id="day61"),
    ]
    result = run(LotCase.model_validate(payload))
    assert result["distributions"][0]["qualified"] == 50


def test_pre_ex_date_sale_cannot_consume_the_remaining_shares_entitlement():
    """Forty shares leave before entitlement, twenty shortly afterward, forty qualify.

    Purchase offsets must advance after each partial sale. Otherwise the earlier
    sale overlaps the later entitlement and attributes the wrong holding period.
    """
    payload = recently_acquired()
    payload["trades"] += [
        trade("sell", "2026-05-20", qty="40", id="before_ex"),
        trade("sell", "2026-06-10", qty="20", id="after_ex"),
    ]
    result = run(LotCase.model_validate(payload))
    assert result["distributions"][0]["amount"] == 60
    assert result["distributions"][0]["qualified"] == 40


def test_wash_tacked_capital_holding_period_does_not_qualify_a_recent_dividend():
    payload = distribution_case()
    payload["trades"] = [
        trade("sell", "2026-05-20", price="7.5", id="old_sale"),
        trade("buy", "2026-05-21", price="7.5", id="replacement"),
        trade("sell", "2026-06-10", price="7.5", id="replacement_sale"),
    ]
    result = run(LotCase.model_validate(payload))
    assert result["disposals"][1]["federal_character"] == "long_term"
    assert result["distributions"][0]["qualified"] == 0
