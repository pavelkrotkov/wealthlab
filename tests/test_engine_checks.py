"""Independent official-rate and analytic cases validate reusable engine mappings."""

import pytest

from wealthlab.checks.report import run, versions


def test_core_engine_cases():
    results = run()
    assert len(results) == 7
    assert all(row["passed"] for row in results)
    assert results[0]["actual"] == pytest.approx(15_898)
    assert results[1]["actual"] == pytest.approx(11_475)
    assert results[2]["actual"] == pytest.approx(3_270)
    assert results[3]["actual"] == pytest.approx(9.925053717274437)
    assert versions()["taxcalc"] == "6.8.5"
