"""An existing policy exit recognizes its gain before reference saving uses the receipt.

Loan principal reduces external surrender cash, not the contract's gross gain.
Adding $8,000 debt therefore changes the receipt from $10,000 to $2,000 while
preserving $5,000 ordinary income and the conditional $500 additional tax.
"""

import pytest

from wealthlab.products.life_comparison import compare
from wealthlab.products.life_comparison_existing import synthetic
from wealthlab.products.life_comparison_inputs import LifeComparison


@pytest.fixture(scope="module")
def cases():
    result = compare(synthetic())
    retain = result["alternatives"]["retain"]["details"][0]["rows"][-1]
    sell = result["alternatives"]["liquid_term"]["details"][0]["rows"][-1]
    return retain, sell


def test_existing_mec_surrender_and_loan_recognize_actual_conditional_taxes(cases):
    retain, sell = cases
    assert retain["net_wealth"] == 56950
    assert retain["tax_position"] == 50
    assert sell["net_wealth"] == 56200
    assert sell["tax_position"] == 500


def test_existing_surrender_cash_and_policy_value_are_not_counted_twice(cases):
    _, sell = cases
    assert sell["closing_cash"] == 54900
    assert sell["account_balances"]["life_policy"] == 0
    assert sell["account_balances"]["brokerage"] == 1800
    assert sell["annual_tax"]["federal"]["insurance_ordinary_income"] == 5000


def test_existing_loan_is_repaid_before_reference_saving_receives_surrender_cash():
    data = synthetic().model_dump(mode="json")
    for scenario in data["alternatives"].values():
        scenario["accounts"][1]["balance"] = "2000"
        scenario["life_plan"]["holdings"][0]["contract"]["opening_loan"] = "8000"
    result = compare(LifeComparison.model_validate(data))
    row = result["alternatives"]["liquid_term"]["details"][0]["rows"][-1]
    assert row["closing_cash"] == 46900
    assert row["net_wealth"] == 48200
    assert row["life_policy_audit"]["executed"][0]["external_cash"] == 2000
    assert row["annual_tax"]["federal"]["insurance_ordinary_income"] == 5000
