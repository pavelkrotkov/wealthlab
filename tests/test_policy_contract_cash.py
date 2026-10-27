"""Actual contract exits preserve capital and taxes, without counting forfeited awards as cash.

The independent identity is330000opening capital +600premium -48000spending
-1ordinary-stock commission -261NJ tax =282338. Federal recognized income
is20600 in2026 and4999 in2027 after the $1 stock commission, below the
supplied joint standard deductions; NJ2027 income3999 is below its filing
threshold. The2026NJ table tax is261.
"""

import pytest
from optimization_contract_cases import case
from optimization_product_cases import case as product_case

from wealthlab.optimization.contract_example import extend
from wealthlab.optimization.inputs import PolicySearch
from wealthlab.optimization.search import search


@pytest.fixture(scope="module")
def result():
    return search(case())


def test_contract_cash_exit_reconciles_independently_in_training_and_validation(result):
    candidate = result["candidates"][0]
    assert candidate["median_real_after_tax_exit_wealth"] == 282338
    assert candidate["median_net_cash_tax"] == 261
    assert result["held_out"]["assessment"]["median_real_after_tax_exit_wealth"] == 282338
    assert result["configured_validation_passed"]
    assert not candidate["issuer_concentration_complete"]


def test_native_audit_separates_real_cash_forfeiture_and_independent_source_income(result):
    rows = result["selected_training"]["details"][0]["rows"]
    state = rows[-1]["employer_tranches"][0]["exit_evidence"]
    assert (state["cash_distributed"], state["forfeited_value"]) == (20000, 80000)
    assert state["contractual_exit_proven"] is True
    assert (rows[11]["annual_tax"]["federal"]["agi"], rows[-1]["annual_tax"]["federal"]["agi"]) == (
        20600,
        4999,
    )
    option = rows[-1]["option_mark_audit"][-1]["exit_state"]
    assert option["modeled_cash_exit_complete"]
    assert option["open_contracts"] == option["stock_lots"] == []
    assert option["cash"] == option["settlement_loan"] == option["collateral"] == 0


def test_contracts_and_existing_products_share_one_actual_wallet_and_complete_exit():
    data = extend(product_case()).model_dump(mode="json")
    for market in (data["training"], data["validation"]):
        for asset in market["assets"]:
            asset.update(expected_annual_mark_return=0, annual_volatility=0, annual_cash_yield=0)
    result = search(PolicySearch.model_validate(data))
    # The four existing product books contribute40000 and return it exactly once.
    assert result["candidates"][0]["median_real_after_tax_exit_wealth"] == 322338
    assert result["held_out"]["assessment"]["median_real_after_tax_exit_wealth"] == 322338
    assert result["configured_validation_passed"]
