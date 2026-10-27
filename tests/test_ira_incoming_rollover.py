"""Incoming20k adds4k federal/6k NJ basis to an existing10k IRA with1k/2k basis.

A later15k withdrawal from30k total assets recovers2.5k/4k, leaving
12.5k/11k taxable. No source receipt becomes ordinary IRA contribution cash.
"""

import pytest

from wealthlab.retirement.distributions import run
from wealthlab.retirement.ira_rollover_example import synthetic


@pytest.fixture(scope="module")
def result():
    return run(synthetic())


def test_confirmed_transfer_and_later_withdrawal_conserve_gross_ira_book_assets(result):
    assert result["incoming_rollover_value"] == 20000
    assert result["cash"] == 15000
    assert result["account_balances"]["ira"] == 15000
    assert result["cash"] + sum(result["account_balances"].values()) == 10000 + 20000
    assert result["contribution_owners"] == []


def test_federal_and_state_basis_follow_independent_owner_wide_reconciliation(result):
    row = result["orders"][0]
    assert row["federal_basis_recovered"] == 2500
    assert row["nj_basis_recovered"] == 4000
    assert row["federal_taxable"] == 12500
    assert row["nj_taxable"] == 11000
    assert result["owners"][0]["federal_ira_basis"] == 2500
    assert result["owners"][0]["nj_ira_basis"] == 4000


def test_transfer_without_distributions_creates_no_cash_or_tax_deduction():
    case = synthetic().model_copy(update=dict(orders=[]))
    result = run(case)
    assert result["cash"] == 0
    assert result["account_balances"]["ira"] == 30000
    assert result["annual_tax"]["additional_liability"] == 0
    assert result["owners"][0]["federal_ira_basis"] == 5000
    assert result["owners"][0]["nj_ira_basis"] == 8000
