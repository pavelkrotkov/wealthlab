"""The complete cash/tax path counts withheld premiums once and reports gross SSA benefits.

January has no issued benefit yet, so its premiums use cash. Subsequent
checks withhold current Part B; credited benefits retain the statutory
rounding adjustment while the tax ledger adds withheld amounts back.
"""

from decimal import Decimal

import pytest

from wealthlab.household.projection import project
from wealthlab.retirement.social_medicare_example import synthetic


@pytest.fixture(scope="module")
def rows():
    return project(synthetic())


def test_ssa_gross_net_and_premiums_conserve_household_wealth(rows):
    gross = sum(r["social_security_gross_credited"] for r in rows)
    net = sum(r["social_security_cash"] for r in rows)
    withheld = sum(r["medicare_benefit_withheld"] for r in rows)
    assert (gross, net, withheld) == (152243, 138040, 14203)
    assert sum(r["medicare_paid"] for r in rows) == Decimal("31888.80")
    assert rows[-1]["net_wealth"] == 200000 + 36000 + gross - 144000 - Decimal("31888.80")
    assert rows[-1]["closing_cash"] == Decimal("112354.20")


def test_january_before_first_benefit_is_direct_paid_then_current_withholding_starts(rows):
    assert rows[0]["social_security_cash"] == rows[0]["medicare_benefit_withheld"] == 0
    assert rows[0]["medicare_cash_paid"] == Decimal("885.80")
    assert rows[1]["social_security_cash"] == 3944
    assert rows[1]["medicare_cash_paid"] == 480
    assert rows[1]["medicare_benefit_withheld"] == Decimal("405.80")


def test_annual_tax_uses_gross_and_retains_smi_rounding_difference(rows):
    assert rows[11]["annual_tax"]["federal"]["gross_social_security"] == Decimal("47847.80")
    assert rows[23]["annual_tax"]["federal"]["gross_social_security"] == Decimal("52197.60")
    assert sum(r["social_security_premium_rounding_change"] for r in rows) == -7
    assert not any(r["funding_failure"] for r in rows)
