"""Funded current-year deposits reconcile cash, annual basis and tax recognition once."""

from decimal import Decimal

import pytest

from wealthlab.retirement.distributions import run
from wealthlab.retirement.ira_contribution_example import synthetic


@pytest.fixture(scope="module")
def result():
    return run(synthetic())


def test_combined_deposits_conserve_cash_and_capital(result):
    assert (result["cash"], result["account_balances"]) == (
        39000,
        dict(ira=Decimal(73000), roth=Decimal(48000)),
    )
    assert result["cash"] + sum(result["account_balances"].values()) == 160000
    assert [r["funded"] for r in result["contribution_orders"]] == [3000, 3000]


def test_federal_and_nj_basis_additions_remain_distinct(result):
    added = result["contribution_owners"][0]
    assert (
        added["federal_ira_deduction"],
        added["new_federal_ira_basis"],
        added["new_nj_ira_basis"],
    ) == (3000, 0, 3000)
    assert (result["owners"][0]["federal_ira_basis"], result["owners"][0]["nj_ira_basis"]) == (
        Decimal("14174.76"),
        Decimal("37563.11"),
    )


def test_current_roth_regular_contribution_precedes_conversion_buckets(result):
    roth = result["orders"][-1]
    assert (roth["federal_taxable"], roth["additional_tax"]) == (0, 1200)
    assert result["owners"][0]["conversions"][0]["taxable_remaining"] == 3000


def test_actual_annual_magi_excludes_deduction_and_roth_conversion_appropriately(result):
    assert result["annual_tax"]["with_distributions"]["federal"]["agi"] == Decimal("121174.76")
    assert result["contribution_eligibility"] == dict(
        status="checked_supported_annual_w2_case",
        traditional_ira_magi=Decimal("124174.76"),
        roth_ira_magi=Decimal("108058.25"),
        eligible_w2_compensation=Decimal(100000),
    )
