"""An IRA conversion cannot satisfy or precede an unmet current-year RMD target."""

import pytest
from test_ira_withdrawals import calculate, payload


def rmd_case():
    data = payload()
    data["owners"][0].update(
        birth_date="1953-06-15",
        federal_ira_basis="0.00",
        nj_ira_basis="0.00",
        roth_regular_basis="0.00",
        nj_roth_basis="0.00",
        conversions=[],
        roth_first_year=None,
    )
    data["accounts"][0]["balance"] = "265000.00"
    data["accounts"][1]["balance"] = "0.00"
    conversion, withdrawal = data["orders"][1], data["orders"][0]
    data["orders"] = [
        dict(conversion, date="2026-01-01"),
        dict(withdrawal, date="2026-02-01"),
        dict(conversion, id="later_conversion", date="2026-03-01"),
    ]
    return data


def test_uniform_rmd_and_conversion_cash_conservation():
    result = calculate(rmd_case())
    assert result["rmd"]["person"]["required"] == 10000  # $265,000 / IRS age-73 divisor 26.5.
    assert result["rmd"]["person"]["shortfall"] == 0
    assert [row["paid"] for row in result["orders"]] == [0, 10000, 20000]
    assert result["orders"][0]["blocked_by_rmd"] is True
    assert result["cash"] == 10000
    assert result["account_balances"] == {"ira": 235000, "roth": 20000}


def test_unmet_rmd_target_is_visible_without_an_automatic_withdrawal():
    data = rmd_case()
    data["orders"] = []
    result = calculate(data)
    assert result["rmd"]["person"]["shortfall"] == 10000
    assert result["cash"] == 0


def test_1959_regulatory_gap_requires_an_explicit_scenario_choice():
    data = rmd_case()
    data.update(year=2032, orders=[])
    data["owners"][0]["birth_date"] = "1959-06-15"
    with pytest.raises(ValueError, match="1959"):
        calculate(data)
    data["owners"][0]["birth_1959_start_age"] = 73
    assert calculate(data)["rmd"]["person"]["required"] == 10000
    data["owners"][0]["birth_1959_start_age"] = 75
    assert calculate(data)["rmd"]["person"]["required"] == 0
