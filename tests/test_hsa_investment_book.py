"""Inside-HSA assets conserve cash, fees and basis independently of personal tax.

The opening USD10,100 acquires USD1,600 price/trade gains and dividend income
relative to opening marks, then pays USD5 commissions and USD50 custody fees.
Separate historical NJ basis yields different recognized gains, not new cash.
"""

from datetime import date
from decimal import Decimal as D

import pytest

from wealthlab.retirement.hsa_investment_example import synthetic
from wealthlab.retirement.hsa_investment_inputs import HSAInvestments
from wealthlab.retirement.hsa_investment_reporting import snapshot
from wealthlab.retirement.hsa_investments import Ledger, run


@pytest.fixture(scope="module")
def result():
    return run(synthetic())


def test_actual_assets_and_costs_conserve_principal(result):
    assert result["cash_by_account"] == {"hsa": 5000}
    assert result["net_wealth"] == 10100 + 1600 - 5 - 50
    assert result["transaction_costs"] == 5
    assert result["fee_summary"]["cash_paid"] == 50
    assert result["fee_summary"]["cash_owed"] == 0
    assert result["cash_targets"][0]["unfilled"] == 0


def test_nj_realization_is_separate_from_federal_exemption_and_unrealized_marks(result):
    assert result["federal_investment_income"] == 0
    assert result["nj_income_by_year"][2026] == dict(
        interest=0, dividends=100, dispositions=D("2490.95")
    )
    assert result["disposals"][0]["nj_basis"] == 2400
    assert result["disposals"][0]["federal_basis"] == 3200
    assert result["disposals"][1]["nj_basis"] == D("960.05")
    assert sum(D(lot["nj_basis"]) for lot in result["lots"]) == D("3640.95")


def test_future_closing_prices_cannot_fund_an_earlier_request():
    ledger = Ledger(synthetic())
    available = ledger.raise_cash("hsa", D(5000), date(2026, 6, 30))
    assert available == 5000
    assert ledger.generated[0]["price"] == "100"
    assert ledger.generated[0]["quantity"] == "10.550000"
    assert snapshot(ledger)["net_wealth"] == 10945


def test_earlier_snapshots_do_not_acquire_future_transactions():
    ledger = Ledger(synthetic())
    ledger.advance(date(2026, 1, 12))
    before = snapshot(ledger)
    ledger.advance(date(2026, 12, 31))
    assert len(before["executed_trades"]) == 1
    assert len(before["disposals"]) == 1
    assert len(snapshot(ledger)["executed_trades"]) == 3


def test_security_lock_preserves_value_without_spendable_cash():
    data = synthetic().model_dump(mode="json")
    data["liquidity_locks"] = [
        dict(
            id="lock",
            provenance="assumption",
            security_id="fund",
            start="2026-12-01",
            end="2027-01-01",
        )
    ]
    locked = run(HSAInvestments.model_validate(data))
    assert locked["cash_by_account"]["hsa"] == 3947
    assert locked["cash_targets"][0]["unfilled"] == 1053
    assert locked["net_wealth"] == 11647
    assert locked["transaction_costs"] == 3
