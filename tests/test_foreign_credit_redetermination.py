"""A later foreign refund retains original-year tax identity and actual receipt cash.

The annual lower bridge cannot revise an already closed US return. It must
retain the receipt and block the affected candidate, including a nominally
denied current-year election, rather than netting old credit into a new year.
"""

from copy import deepcopy
from decimal import Decimal

import pytest

from wealthlab.tax.foreign_credit import evaluate
from wealthlab.tax.foreign_credit_example import amount, synthetic
from wealthlab.tax.foreign_credit_inputs import ForeignCreditCase


@pytest.mark.parametrize("election", ["allowed", "denied"])
def test_later_refund_cannot_become_a_current_year_credit_or_rewrite_paid_cash(election):
    data = synthetic().model_dump(mode="json")
    historical = deepcopy(data["income"])
    for row in historical:
        row["id"] += "_2025"
    for row in data["income"]:
        row["value"]["date"] = "2026-06-30"
    data["income"].extend(historical)
    original = data["tax_cash"][0]
    original["income_ids"] = ["work_es_2025"]
    data["tax_cash"].append(
        dict(
            original,
            id="later_refund",
            kind="refund",
            reverses_id=original["id"],
            value=amount("2026-12-20", 1000, "EUR", "1.10"),
            creditable_native="1000",
        )
    )
    data["annual"]["policy"].update(year=2026, mode="freeze_2025")
    data["annual"]["nj_regime"] = "freeze_2025"
    data.update(as_of="2026-12-31", eligibility=election)
    result = evaluate(ForeignCreditCase.model_validate(data))
    assert result["observed_tax_cash_outflow_usd"] == Decimal(-1100)
    assert result["all_tax_history"][0]["observed_cash_outflow_usd"] == Decimal(11000)
    assert result["actual_tax_cash"][0]["credit_year"] == 2025
    assert result["candidate"] is None
    assert "closed-return" in result["unresolved"][0]
