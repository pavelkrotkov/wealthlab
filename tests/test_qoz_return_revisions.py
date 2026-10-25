"""A late investment corrects source-year tax without rewriting real payments.

The independent capital identity is $100,000 source stock plus $5,000 cash.
The source gain is $80,000 federally and $70,000 in NJ. Fully deferring both
leaves no source-year liability, but the actual earlier payment is returned
only through the later refund queue. No fund return or dividend changes capital.
"""

from datetime import date
from decimal import Decimal

import pytest
from qoz_transition_cases import transition

from wealthlab.household.projection import project
from wealthlab.products.qoz_tax import inclusion_date


@pytest.fixture(scope="module")
def rows():
    return project(transition())


def test_2026_source_gain_timely_invested_in_2027_uses_new_investment_regime(rows):
    audit = rows[-1]["qoz_audit"]
    call = audit["calls"][0]
    assert call["regime"] == "post_2026"
    assert call["source"]["date"] == "2026-12-15"
    assert inclusion_date(audit["tranches"][0]["invested"]) == date(2032, 1, 31)
    assert rows[12]["annual_tax"]["federal"]["agi"] == 0
    assert rows[12]["annual_tax"]["new_jersey"]["total_income"] == 0


def test_source_year_is_revised_but_actual_prior_payment_and_cash_stay_historical(rows):
    revision = rows[-1]["qoz_audit"]["source_return_revisions"][0]
    paid = rows[11]["tax_settlement_paid"]
    assert paid > 0
    assert revision["year"] == 2026
    assert revision["old_result"]["new_jersey"]["total_income"] == Decimal(70000)
    assert revision["final_result"]["total_liability"] == 0
    assert sum(revision["actual_net_paid"].values()) == paid
    assert rows[12]["closing_cash"] == Decimal(105000) - paid - Decimal(80000)


def test_refund_is_received_once_after_investment_becomes_known(rows):
    revision = rows[-1]["qoz_audit"]["source_return_revisions"][0]
    assert revision["refund_scheduled"]["date"] == date(2027, 4, 1)
    assert rows[12]["tax_refund_received"] == 0
    assert rows[15]["tax_refund_received"] == rows[11]["tax_settlement_paid"]
    assert sum(r["tax_refund_received"] for r in rows) == rows[11]["tax_settlement_paid"]
    assert rows[-1]["net_wealth"] == Decimal(105000)
