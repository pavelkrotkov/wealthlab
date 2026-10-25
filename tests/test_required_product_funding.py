"""Required product cash shares actual sale gains, withholding and household bills."""

from datetime import date
from decimal import Decimal as D

import pytest

from tests.test_taxable_funding import scenario
from wealthlab.household.funding import Wallet
from wealthlab.tax.facts import FederalIncome
from wealthlab.tax.nj_facts import NJIncome
from wealthlab.tax.projection_inputs import TaxEvent
from wealthlab.tax.projection_ledger import TaxLedger

START, END = date(2026, 12, 1), date(2027, 1, 1)


def setup(payload):
    household = scenario(payload)
    return TaxLedger(household.tax_plan, household), Wallet(household)


def test_two_product_payments_and_spending_share_one_tax_funding_total(payload):
    ledger, wallet = setup(payload)

    def required_payments(wallet, start, end):
        for due in (D(1000), D(500)):
            ledger.fund_required(wallet, due, start, end)
            assert wallet.pay(due) == due
        return []

    row = ledger.month({}, wallet, START, END, D(10000), receipt_hook=required_payments)
    ledger.close(wallet, START, END)
    assert wallet.pay(D(10000)) == 10000
    # $11,500 needs 1/(1-.15-.0637) gross sales under the supplied marginal rates.
    expected = D(11500) / D(".7863")
    assert abs(row["funding_sale_proceeds"] - expected) <= D(".02")
    assert wallet.balances["brokerage"] == 100000 - row["funding_sale_proceeds"]
    assert wallet.cash <= D(".02")


def test_prior_product_receipt_is_actual_cash_before_later_required_sale(payload):
    ledger, wallet = setup(payload)

    def received_then_paid(wallet, start, end):
        yield TaxEvent(
            date=start,
            description="Actual earlier receipt",
            cash_received=D(1000),
            federal=FederalIncome(),
            new_jersey=NJIncome(),
        )
        ledger.fund_required(wallet, D(1000), start, end)
        assert wallet.pay(D(1000)) == 1000

    row = ledger.month({}, wallet, START, END, D(10000), receipt_hook=received_then_paid)
    ledger.close(wallet, START, END)
    assert row["tax_event_cash"] == 1000
    assert row["funding_sale_proceeds"] == D("12717.79")
    assert wallet.pay(D(10000)) == 10000
    assert wallet.cash == 0


def test_product_funding_cannot_run_outside_the_current_tax_month(payload):
    ledger, wallet = setup(payload)
    with pytest.raises(ValueError, match="active household"):
        ledger.fund_required(wallet, D(1), START, END)
    ledger.month({}, wallet, START, END, D(0))
    with pytest.raises(ValueError, match="active household"):
        ledger.fund_required(wallet, D(1), START, END)


def test_product_cannot_request_negative_cash_or_another_period(payload):
    ledger, wallet = setup(payload)

    def bad_requests(wallet, start, end):
        with pytest.raises(ValueError, match="negative"):
            ledger.fund_required(wallet, D(-1), start, end)
        with pytest.raises(ValueError, match="active household"):
            ledger.fund_required(wallet, D(1), date(2026, 11, 1), end)
        return []

    row = ledger.month({}, wallet, START, END, D(0), receipt_hook=bad_requests)
    assert row["funding_sale_proceeds"] == 0
    assert wallet.balances["brokerage"] == 100000
