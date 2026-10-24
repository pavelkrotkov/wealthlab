"""Employee-plan gains stay invested and leave taxable wages/cash reconciliation intact."""

from test_workplace_market_returns import result as result


def test_growth_is_not_double_counted_as_cash_or_taxable_wages(result):
    rows = result["details"][0]["rows"]
    last = rows[-1]
    assert last["closing_cash"] == 176637
    assert last["annual_tax"]["federal"]["agi"] == 96000
    assert sum(r["market_cash_yield"] for r in rows) == 0
    gain = sum(r["workplace_market_change"] for r in rows)
    assert last["net_wealth"] == 201137 + gain
    assert len(last["workplace_market_audit"]) == 24
