"""Schedule imports are complete replacements with unknown values and explicit confirmation."""

import csv
from io import StringIO

from wealthlab.products.life_illustration_csv import COLUMNS, export, replace
from wealthlab.products.life_illustration_example import synthetic


def csv_text(rows):
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=COLUMNS)
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()


def test_export_import_preserves_amounts_dates_and_missing_values_but_requires_confirmation():
    original = synthetic()
    revised = replace("\ufeff" + export(original), original)
    for before, after in zip(original.illustrations, revised.illustrations, strict=True):
        assert after.flows == before.flows
        assert after.values == before.values
        assert not after.values_match_cashflows_and_funding_path_confirmed
    assert revised.illustrations[-1].values[0].gross_death_benefit is None
    assert original.illustrations[0].values_match_cashflows_and_funding_path_confirmed


def test_single_case_value_schedule_replaced_without_touching_other_case_or_flows():
    original = synthetic()
    rows = [
        dict(
            illustration_id="current",
            record_type="value",
            date="2029-01-01",
            gross_cash_value="2500",
            gross_surrender_value="2400",
        )
    ]
    revised = replace(csv_text(rows), original)
    assert revised.illustrations[0] == original.illustrations[0]
    current = revised.illustrations[1]
    assert current.flows == original.illustrations[1].flows
    assert len(current.values) == 1
    assert current.values[0].gross_surrender_value == 2400
    assert current.values[0].gross_death_benefit is None
