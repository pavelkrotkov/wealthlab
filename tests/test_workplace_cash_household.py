"""The plan loses gross assets while only net receipts can fund household deposits.

A $100,000 plan pays $10,000, of which $2,000 is withheld and $8,000
funds an HSA. This is entirely internal movement: $90,000 remaining plan,
$8,000 HSA and a $2,000 refund receivable preserve $100,000 household wealth.
The age-55 exception applies before the owner's birthday in the separation year.
"""

import pytest

from wealthlab.household.projection import project
from wealthlab.retirement.workplace_withdrawal_example import synthetic


@pytest.fixture(scope="module")
def rows():
    return project(synthetic())


def test_actual_plan_debit_and_net_cash_funding_preserve_household_assets(rows):
    february = rows[1]
    assert february["account_balances"]["work_pretax"] == 90000
    assert february["workplace_withdrawal_gross"] == 10000
    assert february["workplace_withdrawal_net"] == february["hsa_personal_contributions"] == 8000
    assert february["tax_source_withholding"] == 2000
    assert february["closing_cash"] == 0
    assert february["net_wealth"] == 100000


def test_separation_exception_and_delayed_refund_do_not_create_income_or_cash(rows):
    audit = rows[-1]["workplace_withdrawal_audit"][0]
    assert audit["separation_age55_exception"]
    assert audit["below_age59_half"]
    assert audit["additional_tax"] == 0
    assert rows[11]["annual_tax"]["federal"]["agi"] == 2000
    assert rows[11]["tax_refund_receivable"] == 2000
    assert rows[15]["tax_refund_received"] == 2000
    assert rows[-1]["net_wealth"] == 100000


def test_month_end_returns_apply_after_actual_gross_plan_debit():
    data = synthetic().model_dump(mode="json")
    data["workplace_plan"]["returns"] = [
        dict(
            id="feb_return",
            provenance="illustration",
            date="2026-02-28",
            account_id="work_pretax",
            rate=".10",
        )
    ]
    from wealthlab.household.scenario import Scenario

    rows = project(Scenario.model_validate(data))
    assert rows[1]["workplace_market_change"] == 9000
    assert rows[1]["account_balances"]["work_pretax"] == 99000
    assert rows[-1]["net_wealth"] == 109000
