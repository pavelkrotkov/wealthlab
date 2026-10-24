"""Flat HSA prices still realize gains against independently supplied NJ basis.

After the $50 custody fee, opening cash is $50. Funding a $5,000 provider
payment with a $2 commission requires $4,952 gross share proceeds, or 49.52
shares at $100. Their NJ basis is $2,971.20; net proceeds of $4,950 therefore
realize $1,978.80. This is realized gain, not assumed tax paid or price growth.
"""

from decimal import Decimal

import pytest

from wealthlab.markets.household_run import run
from wealthlab.markets.hsa_example import synthetic
from wealthlab.markets.paths import generate


@pytest.fixture(scope="module")
def result():
    household, market, binding = synthetic()
    asset = market.assets[0].model_copy(
        update=dict(
            expected_annual_mark_return=0,
            annual_cash_yield=0,
        )
    )
    market = market.model_copy(update=dict(assets=[asset], expected_annual_inflation=0))
    return run(household, generate(market), binding)


def test_actual_flat_path_bill_funding_and_costs(result):
    rows = result["details"][0]["rows"]
    assert rows[-1]["net_wealth"] == 11100 - 6000 - 2 - 50 == 5048
    assert rows[-1]["medical_provider_paid"] == 5000
    assert rows[-1]["medical_cash_paid"] == 1000
    assert rows[-1]["medical_owed"] == 0
    assert result["aggregate"]["successes"] == 1


def test_realized_gain_uses_independent_nj_basis_despite_flat_prices(result):
    rows = result["details"][0]["rows"]
    audit = rows[-1]["hsa_audit"]["investments"]
    assert audit["nj_income_by_year"][2026] == dict(
        interest=0, dividends=0, dispositions=Decimal("1978.80")
    )
    assert rows[-1]["annual_tax"]["federal"]["agi"] == 0
    assert rows[-1]["annual_tax"]["new_jersey"]["gross_income"] == Decimal("1978.80")


def test_actual_security_exposure_replaces_unmeasured_hsa_account(result):
    row = result["details"][0]["rows"][-1]
    assert row["market_unmapped_factor_accounts"] == []
    assert row["market_unmeasured_issuer_accounts"] == []
    assert row["market_security_values"] == {"hsa:fund": Decimal("5048")}
    assert row["market_factor_values"] == dict(equities=Decimal("5048"))
