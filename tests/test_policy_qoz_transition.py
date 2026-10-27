"""The selected partial subscription wins only through actual source-year revisions and cash."""

import pytest
from optimization_qoz_transition_cases import case

from wealthlab.optimization.search import search


@pytest.fixture(scope="module")
def result():
    return search(case())


def test_two_year_cash_oracle_selects_partial_subscription_with_frozen_heldout_choice(result):
    # No-entry/full/reference pay1247NJ; half pays420in2026plus595in2027.
    assert [c["median_real_after_tax_exit_wealth"] for c in result["candidates"]] == [
        103753,
        103985,
        103753,
        103753,
    ]
    assert result["selection"] == "candidate_1"
    assert result["held_out"]["assessment"]["median_real_after_tax_exit_wealth"] == 103985
    assert result["configured_validation_passed"]


def test_actual_refund_occurs_after_investment_and_only_once(result):
    rows = result["selected_training"]["details"][0]["rows"]
    assert rows[11]["closing_cash"] == 103753
    assert rows[12]["qoz_call_paid"] == 40000
    assert rows[12]["tax_refund_received"] == 0
    assert sum(row["tax_refund_received"] for row in rows) == 827
    assert rows[-1]["closing_cash"] == 103985


def test_canonical_source_return_preserves_revised_liability_without_historical_cash_rewrite(
    result,
):
    rows = result["selected_training"]["details"][0]["rows"]
    audit = rows[-1]["qoz_audit"]
    assert audit["final_source_returns"]["2026"]["new_jersey"]["income_tax"] == 420
    assert rows[11]["tax_settlement_paid"] == 1247
    assert rows[-1]["annual_tax"]["new_jersey"]["income_tax"] == 595
