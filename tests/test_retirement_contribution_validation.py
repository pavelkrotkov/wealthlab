"""Malformed inputs must fail before any scenario cash or account is mutated."""

import pytest
from test_retirement_contributions import calculate, case_for


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("destination", "missing", "contributing owner"),
        ("owner", "missing", "contributing owner"),
        ("date", "2027-01-01", "contribution year"),
        ("provenance", "unresolved", "Resolve contribution"),
        ("id", "person", "unique"),
    ],
)
def test_invalid_contribution_reference_is_rejected(field, value, message):
    data = case_for("traditional_ira")
    data["orders"][0][field] = value
    with pytest.raises(ValueError, match=message):
        calculate(data)


def test_ira_cannot_be_confused_with_workplace_account():
    data = case_for("pretax_401k")
    data["orders"].append(dict(data["orders"][0], id="ira_order", kind="traditional_ira"))
    with pytest.raises(ValueError, match="distinct accounts"):
        calculate(data)
    data["orders"].pop()
    data["orders"][0]["destination"] = "roth"
    with pytest.raises(ValueError, match="wrapper"):
        calculate(data)
