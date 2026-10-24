"""Supported own-benefit cases match Owl; its reproduced spousal discrepancy stays explicit."""

import pytest

from tests.test_social_cash import calculate, payload


@pytest.mark.parametrize(
    ("claim", "year", "expected"),
    [("2022-01-01", 2026, 8400), ("2027-01-01", 2028, 12000), ("2030-01-01", 2031, 14880)],
)
def test_supported_integer_pia_own_case_matches_primary_value_and_owl(claim, year, expected):
    data = payload()
    data.update(start_year=year, end_year=year + 1)
    data["members"] = [data["members"][1]]
    data["members"][0].update(claim_month=claim, partner=None, spousal_eligibility_confirmed=False)
    result = calculate(data)
    comparison = result["owl_comparison"]["rows"][0]
    assert comparison["native_issued"] == comparison["owl_reference"] == expected
    assert comparison["difference"] == 0


def test_reproduced_spousal_drc_reference_gap_does_not_replace_native_cash():
    result = calculate(payload())
    row = next(
        r for r in result["owl_comparison"]["rows"] if r["year"] == 2031 and r["member"] == "spouse"
    )
    assert row["native_issued"] == 15000
    assert row["owl_reference"] == 17880
    assert row["difference"] == -2880


@pytest.mark.parametrize(
    ("field", "value"), [("future_cola_assumption", "0.02"), ("fractional_pia", "1000.90")]
)
def test_incompatible_owl_inputs_are_not_silently_normalized(field, value):
    data = payload()
    if field == "fractional_pia":
        data["members"][1]["pia_january_2026"] = value
    else:
        data[field] = value
    reference = calculate(data)["owl_comparison"]
    assert reference["status"] == "outside_reference_scope"
    assert reference["rows"] == []
