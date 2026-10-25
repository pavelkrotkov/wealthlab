"""Two distinct $246,000 plans cannot share their $10,000 age75 requirements.

Alpha's two subaccounts share one requirement. A $15,000 payment recovers
$10,000 RMD and $5,000 eligible remainder, requiring $1,000+$1,000 withholding.
Beta still needs its own $10,000, with $1,000 RMD withholding. All payments
transfer existing assets, so the zero-liability illustration preserves $492,000.
"""

from decimal import Decimal

import pytest

from wealthlab.household.projection import project
from wealthlab.retirement.workplace_rmd_example import synthetic
from wealthlab.tax.household_reporting import summary


@pytest.fixture(scope="module")
def rows():
    return project(synthetic())


def test_plan_groups_and_eligible_remainder_drive_actual_withholding(rows):
    feb = rows[1]
    assert feb["workplace_rmd_required"] == 20000
    assert feb["workplace_rmd_remaining"] == 10000
    assert feb["tax_source_withholding"] == 2000
    assert feb["closing_cash"] == 13000
    audit = rows[-1]["workplace_withdrawal_audit"][0]
    assert audit["rmd_portion"] == 10000
    assert audit["eligible_remainder"] == 5000


def test_december_catchup_does_not_withdraw_from_an_already_satisfied_plan(rows):
    december = rows[11]
    assert december["workplace_withdrawal_gross"] == 10000
    assert december["tax_source_withholding"] == 1000
    assert december["workplace_rmd_remaining"] == december["workplace_rmd_shortfall"] == 0
    assert december["account_balances"]["alpha_one"] == 108000
    assert december["account_balances"]["beta"] == 236000
    assert december["tax_refund_receivable"] == 3000


def test_following_year_uses_actual_closing_assets_without_excess_withdrawal_credit(rows):
    audit = rows[-1]["workplace_rmd_audit"]
    assert audit[2]["required"] == Decimal("9746.84")
    assert audit[3]["required"] == Decimal("9957.81")
    assert rows[12]["workplace_rmd_required"] == Decimal("19704.65")
    assert rows[15]["tax_refund_received"] == 3000
    assert rows[-1]["net_wealth"] == 492000
    report = summary(rows)
    assert report["reported_tax_liability"] == 0
    assert report["gross_cash_taxes_paid"] == Decimal("4970.46")
