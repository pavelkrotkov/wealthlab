"""Reject malformed or ambiguous schedule data before replacing any policy."""

import pytest

from tests.test_life_illustration_csv import csv_text
from wealthlab.products.life_illustration_csv import COLUMNS, replace
from wealthlab.products.life_illustration_example import synthetic


@pytest.mark.parametrize(
    "row,message",
    [
        (dict(illustration_id="unknown", record_type="flow"), "known illustration_id"),
        (dict(illustration_id="current", record_type="unknown"), "record_type"),
        (dict(illustration_id="current", record_type="value", amount="100"), "cannot contain"),
        (
            dict(illustration_id="current", record_type="flow", gross_cash_value="100"),
            "cannot contain",
        ),
    ],
)
def test_ambiguous_csv_rows_rejected(row, message):
    with pytest.raises(ValueError, match=message):
        replace(csv_text([row]), synthetic())


@pytest.mark.parametrize(
    "text,message",
    [
        ("date,amount\n2026-01-01,100", "header"),
        (csv_text([]), "no rows"),
        (csv_text([]) + "current,flow\n", "missing cells"),
        (csv_text([]) + "," * len(COLUMNS), "extra or missing"),
    ],
)
def test_csv_shape_errors_do_not_partially_import(text, message):
    with pytest.raises(ValueError, match=message):
        replace(text, synthetic())
