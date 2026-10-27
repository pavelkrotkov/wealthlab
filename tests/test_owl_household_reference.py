"""Independent full retirement-policy replay with pinned 2026 forecast values.

The exact opening-year match does not conceal later forecast differences.
A cumulative tax difference explains the whole marked-wealth difference;
OWL internal taxable-account redeposits must never become extra income.
"""

from datetime import date
from decimal import Decimal as D

import pytest

from wealthlab.retirement.owl_household_inputs import synthetic
from wealthlab.retirement.owl_household_reference import run

pytestmark = pytest.mark.skipif(date.today().year != 2026, reason="Pinned 2026 forecast values")


@pytest.fixture(scope="module")
def baseline():
    return run(synthetic())


def test_real_withdrawals_tax_and_wealth_reconcile(baseline):
    rows = baseline["rows"]
    assert [r["reference_retirement_withdrawal"] for r in rows] == [74550, 50900, 74550]
    assert [r["native_federal_tax"] for r in rows] == [D(5800), D("2890.92"), D("5665.49")]
    assert [r["reference_federal_tax"] for r in rows] == [5800, 2962, 5800]
    assert rows[-1]["native_marked_wealth"] == D("115643.59")
    assert rows[-1]["reference_marked_wealth"] == 115438
    assert rows[-1]["cumulative_tax_difference"] == D("-205.59")


def test_replay_feasibility_and_accounting(baseline):
    assert baseline["max_absolute_wealth_residual"] == 0
    assert not baseline["funding_failure"]
    assert baseline["unfilled_ira_requests"] == 0


def test_no_redeposit_or_deduction_double_count(baseline):
    months = baseline["household_months"]
    assert sum(r["ira_withdrawal_cash"] for r in months) == 200000
    assert sum(r["tax_event_cash"] for r in months) == 200000
    assert sum(r["essential"] for r in months) == 90000
    row = baseline["rows"][0]
    assert row["native_standard_deduction"] + row["native_senior_deduction"] == 24150
