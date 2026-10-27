"""A source-paid credit preserves wealth while remaining unavailable until refund.

Opening assets are zero. The $10,000 external pension creates $8,000 cash
and a $2,000 tax credit. With no resulting liability, that credit becomes an
April refund. HSA funding is an internal transfer, never another cash receipt.
"""

import pytest

from wealthlab.household.projection import project
from wealthlab.tax.household_reporting import summary
from wealthlab.tax.source_example import synthetic


@pytest.fixture(scope="module")
def rows():
    return project(synthetic())


def test_only_net_pension_cash_funds_the_hsa(rows):
    february = rows[1]
    assert february["tax_event_cash"] == 8000
    assert february["hsa_personal_contributions"] == 8000
    assert february["closing_cash"] == 0
    assert february["tax_source_withholding"] == 2000
    assert february["tax_payment_gap"] == 0
    assert february["net_wealth"] == 10000


def test_source_credit_survives_close_and_only_becomes_cash_next_april(rows):
    assert rows[11]["tax_refund_receivable"] == 2000
    assert rows[14]["closing_cash"] == 0
    assert rows[15]["tax_refund_received"] == rows[15]["closing_cash"] == 2000
    assert rows[15]["tax_refund_receivable"] == 0
    assert rows[-1]["account_balances"]["cash_hsa"] == 8000
    assert rows[-1]["net_wealth"] == 10000
    assert sum(row["tax_source_withholding"] for row in rows) == 2000


def test_reporting_counts_source_tax_once_and_keeps_refund_cash_separate(rows):
    report = summary(rows)
    assert report["gross_cash_taxes_paid"] == 2000
    assert report["cash_tax_refunds_received"] == 2000
    assert report["net_cash_taxes_paid"] == report["reported_tax_liability"] == 0
    receipt = rows[1]["tax_source_receipts"][0]
    assert receipt["gross_cash"] == receipt["net_cash"] + receipt["total_withheld"]
