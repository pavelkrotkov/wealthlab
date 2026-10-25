"""A5000 nonqualified plan payment from9400cost/10000value recovers4700, not5000."""

import pytest

from wealthlab.household.projection import project
from wealthlab.retirement.workplace_roth_example import synthetic


@pytest.fixture(scope="module")
def rows():
    return project(synthetic())


def test_nonqualified_designated_roth_cash_uses_plan_pro_rata_not_ira_ordering(rows):
    row = rows[-1]["workplace_roth_audit"][0]
    assert row["gross"] == 5000
    assert row["federal_basis_recovered"] == 4700
    assert row["federal_taxable"] == 300
    assert row["nj_basis_recovered"] == 4500
    assert row["nj_taxable"] == 500
    assert row["additional_tax"] == 30


def test_source_withholding_is_not_extra_wallet_cash_or_extra_tax(rows):
    assert rows[1]["account_balances"] == dict(cash=4940, work_roth=5000)
    assert rows[1]["tax_source_withholding"] == 60
    assert rows[11]["net_wealth"] == 9970
    assert rows[15]["account_balances"] == dict(cash=4970, work_roth=5000)
    assert rows[-1]["net_wealth"] == 9970


def test_independent_remaining_cost_carries_across_years_without_creating_value(rows):
    contract = rows[-1]["workplace_roth_contracts"][0]
    assert contract["federal_basis"] == 4700
    assert contract["nj_basis"] == 4500
    assert contract["value"] == 5000
