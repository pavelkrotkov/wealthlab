"""Closed-return positions follow real later cash without rewriting original payments.

The first case owes tax with no cash, then pays arrears in the next year.
The second starts with already-paid estimates and receives its actual refund
later. Both exercise the real monthly tax ledger rather than a mocked balance.
"""

from datetime import date
from decimal import Decimal

from wealthlab.household.calendar import months
from wealthlab.household.funding import Wallet
from wealthlab.household.scenario import Scenario
from wealthlab.portfolio.household_example import synthetic
from wealthlab.tax.projection_ledger import TaxLedger


def empty_household():
    data = synthetic().model_dump(mode="json")
    data.update(lot_plan=None, incomes=[], expenses=[])
    data["accounts"] = [data["accounts"][0]]
    data["accounts"][0]["balance"] = "0"
    data["tax_plan"]["income_rules"] = []
    return data


def advance(taxes, wallet, start, end):
    row = taxes.month({}, wallet, start, end, Decimal(0))
    row.update(taxes.close(wallet, start, end))
    return row


def test_later_arrears_payments_credit_the_original_closed_tax_year():
    data = empty_household()
    first = data["tax_plan"]["cases"][0]
    first["federal_income"]["interest"] = "50000"
    first["nj_income"]["interest"] = "50000"
    case = Scenario.model_validate(data)
    taxes, wallet = TaxLedger(case.tax_plan, case), Wallet(case)
    for start, end in months(case.start, date(2027, 1, 1)):
        advance(taxes, wallet, start, end)
    position = taxes.closed_returns[2026]
    original_owed = sum(position.positions()[0].values())
    wallet.deposit(Decimal(1000))
    row = advance(taxes, wallet, date(2027, 1, 1), date(2027, 2, 1))
    assert row["prior_tax_paid"] == 1000
    assert sum(position.net_paid.values()) == 1000
    assert sum(position.positions()[0].values()) == original_owed - 1000
    assert position.case.payments.federal_estimates == 0


def test_received_refund_removes_the_closed_receivable_once():
    data = empty_household()
    data["tax_plan"]["cases"][0]["payments"].update(federal_estimates="1000", nj_estimates="500")
    case = Scenario.model_validate(data)
    taxes, wallet = TaxLedger(case.tax_plan, case), Wallet(case)
    for start, end in months(case.start, date(2027, 5, 1)):
        row = advance(taxes, wallet, start, end)
    position = taxes.closed_returns[2026]
    assert row["tax_refund_received"] == 1500
    assert position.net_paid == dict(federal=0, new_jersey=0)
    assert position.positions()[1] == dict(federal=0, new_jersey=0)
    assert_refund_source(taxes.refund_receipts)
    assert wallet.cash == 1500


def assert_refund_source(receipts):
    receipt = next(r for r in receipts if r["cash"])
    assert receipt["source_year"] == 2026
    assert receipt["components"] == dict(federal=1000, new_jersey=500)
