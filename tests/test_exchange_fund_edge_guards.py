"""Incomplete early-tax and invalid basis instructions block favorable simulated cash outcomes."""

from datetime import date

import pytest
from exchange_fund_cases import change, flat

from wealthlab.household.projection import project
from wealthlab.products.exchange_fund_example import request
from wealthlab.products.exchange_fund_household import Ledger


def test_early_cash_exit_requires_request_specific_tax_confirmation():
    def configure(data):
        data["exchange_fund_plan"].update(
            early_redemption="cash_with_supplied_tax",
            requests=[request("early", date(2026, 1, 31), "redeem")],
        )

    with pytest.raises(ValueError, match="request-specific"):
        project(change(flat(), configure))


def test_supplied_basis_reduction_cannot_create_negative_outside_basis():
    def configure(data):
        data["exchange_fund_plan"]["observations"][0]["federal_basis_adjustment"] = "-20001"

    with pytest.raises(ValueError, match="negative partnership basis"):
        project(change(flat(), configure))


def test_taxable_exchange_loss_requires_a_separate_legal_adapter():
    def configure(data):
        data["exchange_fund_plan"].update(federal_contribution="denied")
        data["exchange_fund_plan"]["source_lot"]["federal_basis"] = "150000"

    with pytest.raises(ValueError, match="loss contributions"):
        Ledger(change(flat(), configure))


def test_ordinary_account_fees_cannot_duplicate_exchange_contract_charges():
    def configure(data):
        data["accounts"][1]["monthly_fee"] = "1"

    with pytest.raises(ValueError, match="without other fees"):
        Ledger(change(flat(), configure))
