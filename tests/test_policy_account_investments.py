"""Actual share exits and Roth cost recovery feed native tax and terminal wealth.

Invested HSA withdrawals cost one real commission and recover9999 rather
than the requested10000. The independent Roth variant consumes9400federal
cost and9000NJ cost, leaving600/1000income and60age-based additional tax.
"""

from decimal import Decimal

import pytest
from optimization_account_investments import invested, roth

from wealthlab.optimization.account_exits import hsa_closed
from wealthlab.optimization.search import search


@pytest.fixture(scope="module")
def result():
    return search(invested())


def test_actual_invested_hsa_exit_pays_commission_and_leaves_no_hidden_position(result):
    assert [c["median_real_after_tax_exit_wealth"] for c in result["candidates"]] == [
        270998,
        270998,
    ]
    rows = result["selected_training"]["details"][0]["rows"]
    assert sum(r["hsa_withdrawal_cash"] for r in rows) == 9999
    audit = rows[-1]["hsa_audit"]["investments"]
    assert audit["transaction_costs"] == 1
    assert all(Decimal(lot["quantity"]) == 0 for lot in audit["lots"])
    assert hsa_closed(invested().household, rows[-1])


def test_roth_plan_exit_recovers_independent_basis_and_recognizes_actual_age_tax():
    result = search(roth())
    assert [c["median_real_after_tax_exit_wealth"] for c in result["candidates"]] == [
        271939,
        271939,
    ]
    rows = result["selected_training"]["details"][0]["rows"]
    assert sum(r["workplace_roth_withdrawal_net"] for r in rows) == 9880
    assert sum(r["workplace_roth_additional_tax"] for r in rows) == 60
