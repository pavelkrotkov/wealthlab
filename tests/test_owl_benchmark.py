"""Optional benchmark runs in CI with the benchmarks extra installed."""

import pytest

from wealthlab.checks.report import run


def test_cash_conservation():
    pytest.importorskip("owlplanner")
    result = run(include_retirement=True)[-1]
    assert result["passed"]
    assert result["expected"] > 0
