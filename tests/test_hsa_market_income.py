"""Cash yield stays inside an HSA and changes actual shares sold, not federal income."""

from decimal import Decimal

from wealthlab.markets.household_run import run
from wealthlab.markets.hsa_example import synthetic
from wealthlab.markets.paths import generate


def test_twelve_actual_inside_hsa_interest_receipts_replace_entered_dividend():
    household, market, binding = synthetic()
    asset = market.assets[0].model_copy(
        update=dict(
            expected_annual_mark_return=0,
            annual_cash_yield=0.12,
        )
    )
    market = market.model_copy(update=dict(assets=[asset], expected_annual_inflation=0))
    item = binding.hsa_securities[0].model_copy(update=dict(nj_cash_character="interest"))
    binding = binding.model_copy(update=dict(hsa_securities=[item]))
    result = run(household, generate(market), binding)
    rows = result["details"][0]["rows"]
    audit = rows[-1]["hsa_audit"]["investments"]
    assert audit["nj_income_by_year"][2026] == dict(
        interest=1200, dividends=0, dispositions=Decimal("1498.80")
    )
    assert rows[-1]["net_wealth"] == 6248
    assert rows[-1]["annual_tax"]["federal"]["agi"] == 0
    assert sum(r["tax_event_cash"] for r in rows) == 0
    assert len(audit["distributions"]) == 12
