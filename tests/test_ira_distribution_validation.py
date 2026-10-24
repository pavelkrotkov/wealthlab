"""Incorrect account identity or missing history cannot produce a tax projection."""

import pytest
from test_ira_withdrawals import calculate, payload


@pytest.mark.parametrize(
    ("table", "field", "value", "message"),
    [
        ("orders", "source", "unknown", "Unknown distribution"),
        ("orders", "date", "2027-01-01", "selected year"),
        ("orders", "provenance", "unresolved", "Resolve distribution"),
        ("accounts", "wrapper", "cash", "IRAs only"),
        ("accounts", "owner", "unknown", "known owners"),
        ("owners", "roth_first_year", None, "first Roth contribution"),
        ("owners", "roth_first_year", 2024, "cannot precede"),
    ],
)
def test_missing_or_inconsistent_input_blocks_calculation(table, field, value, message):
    data = payload()
    data[table][0][field] = value
    with pytest.raises(ValueError, match=message):
        calculate(data)


def test_conversion_cannot_transfer_between_owners_or_be_paid_as_cash():
    data = payload()
    data["orders"][1]["destination"] = None
    with pytest.raises(ValueError, match="Roth IRA"):
        calculate(data)
    data = payload()
    data["orders"][0]["destination"] = "roth"
    with pytest.raises(ValueError, match="only conversions"):
        calculate(data)


def test_mixed_qualified_nj_roth_case_is_explicitly_unsupported():
    data = payload()
    data["owners"][0]["birth_date"] = "1966-12-15"
    first = dict(data["orders"][2], amount="1000.00", date="2026-06-14")
    data["orders"] = [first, dict(first, id="qualified", date="2026-06-15")]
    with pytest.raises(ValueError, match="Mixed qualified/nonqualified"):
        calculate(data)


def test_incomplete_opening_context_cannot_be_assumed_away():
    data = payload()
    data["opening_context_complete"] = False
    with pytest.raises(ValueError, match="Confirm complete IRA"):
        calculate(data)
