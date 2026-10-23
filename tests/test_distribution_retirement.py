"""Internal retirement-account fund losses do not invoke taxable investor loss adjustments."""

from distribution_cases import distribution_case, trade

from wealthlab.portfolio.cases import LotCase
from wealthlab.portfolio.engine import run


def test_roth_fund_receipt_and_loss_remain_inside_the_wrapper():
    payload = distribution_case()
    payload["as_of"] = "2026-05-01"
    payload["accounts"][0]["wrapper"] = "roth_ira"
    payload["lots"][0].update(acquired="2026-05-01", federal_holding_start="2026-05-01")
    payload["securities"][0]["kind"] = "etf"
    payload["distributions"][0].update(federal_character="long_term", qualified_fraction="0")
    payload["trades"] = [trade("sell", "2026-06-10", price="5")]
    result = run(LotCase.model_validate(payload))
    assert result["closing_cash"] == 1600
    assert result["annual_tax_comparison"][0]["incremental_liability"] == 0
    assert result["disposals"][0]["federal_recognized_gain"] == 0
