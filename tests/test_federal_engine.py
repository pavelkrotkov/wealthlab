"""Cached policy state must match fresh calculators across years and households."""

from concurrent.futures import ThreadPoolExecutor

import pytest
from taxcalc import Calculator, Policy

from wealthlab.tax.federal import OUTPUTS
from wealthlab.tax.federal_engine import cached_values, records, values


def case(status, wages):
    return dict(
        RECID=1,
        MARS=status,
        age_head=45,
        age_spouse=40 if status == 2 else 0,
        e00200=wages,
        e00200p=wages,
        e00200s=0,
        XTOT=2 if status == 2 else 1,
    )


@pytest.mark.parametrize(
    ("year", "status", "wages"),
    [(2025, 2, 500000), (2026, 1, 80000), (2025, 1, 0), (2025, 2, 150000)],
)
def test_reset_matches_fresh_package_calculator(year, status, wages):
    # Disturb the reusable calculator first with a different filing unit and income.
    values(case(2, 900000), year, OUTPUTS)
    data = case(status, wages)
    reference = Calculator(policy=Policy(), records=records(data, year))
    reference.advance_to_year(year)
    reference.calc_all()
    expected = {name: float(reference.array(name)[0]) for name in OUTPUTS}
    assert values(data, year, OUTPUTS) == expected


def test_concurrent_callers_do_not_share_household_arrays():
    cases = [case(2, 150000), case(1, 90000), case(2, 0), case(1, 600000)]
    expected = [values(data, 2025, OUTPUTS) for data in cases]
    cached_values.cache_clear()
    with ThreadPoolExecutor(max_workers=4) as pool:
        actual = list(pool.map(lambda data: values(data, 2025, OUTPUTS), cases))
    assert actual == expected
