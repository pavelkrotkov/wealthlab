"""A real refund revises original paid-year tax and used carry before optional saving.

Earlier native payments remain historical cash facts. The observed refund
creates a separate receipt, receipt-year FX income and new US arrears; neither
vintage is reset to the receipt year. Retried callbacks cannot debit it twice.
"""

from decimal import Decimal

import pytest
from foreign_redetermination_cases import synthetic_refund

from wealthlab.household.projection import project


@pytest.fixture(scope="module")
def execution():
    observed = []
    rows = project(synthetic_refund(), tax_observer=observed.append)
    return {row["date"]: row for row in rows}, observed


def test_real_refund_revises_paid_year_and_consumed_carry_without_backdating_cash(execution):
    months, _ = execution
    june = months["2027-06-01"]
    assert june["foreign_tax_refund_received"] == 7000
    assert june["prior_tax_paid"] == 5500
    assert june["foreign_tax_cash_records"][0]["refund_fx_difference_usd"] == 1500
    revisions = june["foreign_return_revisions"]
    assert [r["year"] for r in revisions] == [2025, 2026]
    assert [r["final_result"]["federal"]["foreign_tax_credit"] for r in revisions] == [5500, 0]


def test_prior_tax_precedes_optional_saving_and_keeps_original_payment_inputs(execution):
    months, observed = execution
    june, before = months["2027-06-01"], months["2027-05-01"]
    assert june["account_balances"]["saved_cash"] - before["account_balances"]["saved_cash"] == 1500
    final = observed[-1]["closed_returns"]
    assert final[2025].case.payments.federal_estimates == Decimal("6724.50")
    assert final[2025].net_paid["federal"] == Decimal("15599.00")
    assert final[2026].case.foreign_credits.regular == 0
    assert final[2026].net_paid["federal"] == 21099


def test_resolved_actual_refund_has_no_second_debit_or_stale_unknown_credit(execution):
    months, _ = execution
    june, july = months["2027-06-01"], months["2027-07-01"]
    assert not june["foreign_tax_unresolved"]
    assert june["closing_cash"] == 0
    assert july["prior_tax_paid"] == july["foreign_tax_refund_received"] == 0
    assert not july["foreign_return_revisions"]
