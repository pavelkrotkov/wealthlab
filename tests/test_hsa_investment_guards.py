"""Unsupported HSA tax/ownership/wash profiles must not inherit generic IRA behavior."""

from datetime import date
from decimal import Decimal

import pytest

from wealthlab.portfolio.engine import run as generic_run
from wealthlab.retirement.hsa_investment_example import synthetic
from wealthlab.retirement.hsa_investment_inputs import HSAInvestments
from wealthlab.retirement.hsa_investments import Ledger, run


@pytest.mark.parametrize(
    "flag",
    [
        "complete_positions_and_state_basis_confirmed",
        "conditional_state_treatment_confirmed",
        "no_identical_outside_trading_confirmed",
        "fees_are_custodian_charges_confirmed",
        "ordinary_securities_no_ubti_confirmed",
    ],
)
def test_incomplete_profile_is_not_an_exempt_tax_result(flag):
    data = synthetic().model_dump(mode="json")
    data[flag] = False
    with pytest.raises(ValueError, match="Confirm HSA positions"):
        run(HSAInvestments.model_validate(data))


def test_generic_lot_entrypoint_refuses_hsa_ira_semantics():
    with pytest.raises(ValueError, match="dedicated investment book"):
        generic_run(synthetic().case)


@pytest.mark.parametrize(
    "field,value,message",
    [
        ("wrapper", "traditional_ira", "HSA accounts only"),
        ("owner", "joint", "individual ownership"),
    ],
)
def test_mixed_or_joint_accounts_do_not_enter_hsa_book(field, value, message):
    data = synthetic().model_dump(mode="json")
    data["case"]["accounts"][0][field] = value
    with pytest.raises(ValueError, match=message):
        run(HSAInvestments.model_validate(data))


def test_invalid_request_does_not_advance_or_mutate_the_ledger():
    ledger = Ledger(synthetic())
    with pytest.raises(ValueError, match="nonnegative"):
        ledger.raise_cash("hsa", Decimal(-1), date(2026, 12, 31))
    assert ledger.when == date(2026, 1, 1)
    assert ledger.book.history == []


def test_contradictory_final_quote_is_not_silently_overridden():
    data = synthetic().model_dump(mode="json")
    data["marks"].append(dict(date="2026-12-31", prices=dict(fund="120")))
    with pytest.raises(ValueError, match="match the declared closing"):
        run(HSAInvestments.model_validate(data))
