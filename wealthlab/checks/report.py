"""Run independent engine cases and retain actual values and tolerances."""

from importlib.metadata import version
from time import perf_counter

from wealthlab.checks import federal, new_jersey, options


def run(include_retirement: bool = False) -> list[dict]:
    started = perf_counter()
    cases = federal.cases() + options.cases() + new_jersey.cases()
    if include_retirement:
        from wealthlab.checks import retirement

        cases += retirement.cases()
    elapsed = perf_counter() - started
    return [
        {
            "case": name,
            "actual": actual,
            "expected": expected,
            "tolerance": 0.01,
            "batch_seconds": elapsed,
            "passed": abs(actual - expected) <= 0.01,
        }
        for name, actual, expected in cases
    ]


def versions() -> dict[str, str]:
    return {name: version(name) for name in ("taxcalc", "QuantLib", "streamlit")}
