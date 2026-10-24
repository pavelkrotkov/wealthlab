"""Annual tax ordering must not lend future conversion assets to earlier cash requests."""

from test_ira_withdrawals import calculate, payload


def case():
    data = payload()
    data["owners"][0].update(roth_regular_basis="0.00", nj_roth_basis="0.00", conversions=[])
    data["orders"] = [
        dict(data["orders"][2], date="2026-06-01"),
        dict(data["orders"][1], date="2026-12-01"),
    ]
    return data


def test_later_conversion_changes_annual_character_but_not_cash_funding():
    result = calculate(case())
    row = result["orders"][0]
    assert row["paid"] == 25000
    assert row["federal_taxable"] == 5000
    assert row["conversion_recapture"] == 16000
    assert row["additional_tax"] == 2100
    assert result["cash"] == 25000


def test_future_conversion_cannot_fund_previous_empty_roth():
    data = case()
    data["accounts"][1]["balance"] = "0.00"
    result = calculate(data)
    assert result["orders"][0]["paid"] == 0
    assert result["orders"][0]["unfilled"] == 25000
    assert result["orders"][0]["federal_taxable"] == 0
    assert result["cash"] == 0
    assert result["account_balances"]["roth"] == 20000
