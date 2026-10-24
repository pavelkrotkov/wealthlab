"""External payments and full-loss exits reconcile without inventing spendable cash.

An institution payment is a beneficiary distribution for tax reporting even
when the beneficiary belongs to the household. It remains an external payment.
A loss account returns principal first; its excess basis is not a cash asset.
"""

from tests.test_education_cash import calculate, payload


def test_institution_payment_is_beneficiary_income_and_never_parent_cash():
    data = payload()
    data["people"][1]["household_cash_member"] = True
    data["withdrawals"][1]["payee"] = "institution"
    result = calculate(data)
    assert result["external_disbursements"] == 5000
    assert result["annual_tax_groups"][1]["recipient"] == "student"
    data["withdrawals"][1]["payee"] = "beneficiary"
    result = calculate(data)
    assert result["external_disbursements"] == 0
    assert result["cash"] == 20000


def test_loss_exit_records_unrecovered_basis_without_deducting_it():
    data = payload()
    data.update(contributions=[], returns=[], allocations=[])
    data["accounts"][0].update(balance=10000, contribution_basis=15000)
    data["withdrawals"] = [data["withdrawals"][0]]
    result = calculate(data)
    assert result["account_balances"]["college"] == 0
    assert result["contribution_basis"]["college"] == 0
    assert result["closed_account_loss_basis"] == 5000
    assert result["orders"][0]["unfilled"] == 5000
    assert result["annual_tax_groups"][0]["federal_taxable_earnings"] == 0


def test_zero_value_unfunded_request_does_not_erase_basis_before_a_later_deposit():
    data = payload()
    data.update(opening_cash=100, allocations=[])
    data["accounts"][0].update(balance=100, contribution_basis=100)
    data["returns"][0]["rate"] = -1
    data["contributions"][0].update(date="2026-11-01", amount=25)
    data["withdrawals"] = [data["withdrawals"][0]]
    result = calculate(data)
    assert result["cash"] == 75
    assert result["account_balances"]["college"] == 25
    assert result["contribution_basis"]["college"] == 125
    assert result["closed_account_loss_basis"] == 0
