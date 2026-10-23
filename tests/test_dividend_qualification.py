"""Qualified treatment follows actual share holding days, including partially sold ranges."""

from distribution_cases import distribution_case, trade

from wealthlab.portfolio.cases import LotCase
from wealthlab.portfolio.engine import run


def recently_acquired():
    payload = distribution_case()
    payload["lots"] = []
    payload["trades"] = [trade("buy", "2026-05-15")]
    return payload


def test_short_held_dividend_is_ordinary_even_with_an_eligible_issuer():
    payload = recently_acquired()
    payload["trades"].append(trade("sell", "2026-06-10"))
    result = run(LotCase.model_validate(payload))
    federal = result["annual_tax_comparison"][0]["distribution_federal"]
    assert federal == dict(dividends=100, qualified_dividends=0)


def test_partial_sale_qualifies_only_the_shares_held_long_enough():
    payload = recently_acquired()
    payload["trades"].append(trade("sell", "2026-06-10", qty="40"))
    result = run(LotCase.model_validate(payload))
    assert result["annual_tax_comparison"][0]["distribution_federal"]["qualified_dividends"] == 60
    assert result["distributions"][0]["qualified"] == 60


def test_future_holding_days_are_pending_until_observed():
    payload = recently_acquired()
    payload["end"] = "2026-06-20"
    early = run(LotCase.model_validate(payload))
    assert early["annual_tax_comparison"][0]["qualification_pending"] == 100
    assert early["distributions"][0]["qualified"] == 0
    payload["end"] = "2026-07-15"
    later = run(LotCase.model_validate(payload))
    assert later["annual_tax_comparison"][0]["qualification_pending"] == 0
    assert later["distributions"][0]["qualified"] == 100


def test_unconfirmed_risk_or_issuer_never_grants_qualified_treatment():
    payload = distribution_case()
    payload["distributions"][0]["undiminished_risk_confirmed"] = False
    result = run(LotCase.model_validate(payload))
    assert result["distributions"][0]["qualified"] == 0
