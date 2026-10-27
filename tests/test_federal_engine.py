"""Cached policy state must match fresh calculators across years and households."""

import pytest
from taxcalc import Calculator, Policy

from wealthlab.tax.federal import OUTPUTS
from wealthlab.tax.federal_engine import records, values


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
