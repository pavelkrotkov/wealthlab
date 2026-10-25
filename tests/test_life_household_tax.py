"""MEC tax, actual source withholding and delayed refunds share the household return.

The synthetic owner's ordinary policy income is below the standard deduction,
so the only federal liability is the $50 additional tax. Moving that liability
from accrued debt to paid cash cannot change the $56,950 after-tax wealth.
Withholding $100 instead creates a $50 claim; the claim is not spendable cash.
"""

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.products.life_household_example import synthetic


def mec_data(timing="year_end"):
    data = synthetic().model_dump(mode="json")
    contract = data["life_plan"]["holdings"][0]["contract"]
    contract.update(federal_status="mec", opening_federal_basis="8000")
    data["tax_plan"]["settlement_timing"] = timing
    return data


def test_deemed_mec_loan_income_and_additional_tax_are_recognized_once():
    rows = project(Scenario.model_validate(mec_data()))
    final = rows[-1]
    assert final["closing_cash"] == 45500
    assert final["annual_tax"]["federal"]["insurance_ordinary_income"] == 500
    assert final["annual_tax"]["federal"]["insurance_additional_tax"] == 50
    assert final["tax_position"] == 50
    assert final["net_wealth"] == 56950
    assert final["life_policy_values"][0]["federal_basis"] == 10500


def test_monthly_tax_payment_reduces_actual_cash_but_not_wealth_twice():
    rows = project(Scenario.model_validate(mec_data("monthly_accrued")))
    final = rows[-1]
    assert final["closing_cash"] == 45450
    assert final["tax_settlement_paid"] == 50
    assert final["tax_position"] == 0
    assert final["net_wealth"] == 56950


def test_withheld_loan_cash_is_not_spendable_and_overpayment_remains_a_claim():
    data = mec_data()
    data["life_plan"]["holdings"][0]["withholding"] = {
        "loan": {"gross_cash": "500", "federal_income_withheld": "100", "nj_withheld": "0"}
    }
    final = project(Scenario.model_validate(data))[-1]
    assert final["life_cash_received"] == 400
    assert final["life_source_tax_withheld"] == 100
    assert final["closing_cash"] == 45400
    assert final["tax_position"] == -50
    assert final["tax_refund_received"] == 0
    assert final["net_wealth"] == 56950
