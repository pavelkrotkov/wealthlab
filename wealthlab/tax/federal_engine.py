"""Reuse expensive policy initialization while replacing every household record array."""

from functools import lru_cache
from threading import RLock

import pandas as pd
from taxcalc import Calculator, Policy, Records

# ponytail: one local-process lock; batch records if simulations need parallel throughput.
LOCK = RLock()


def records(data: dict, year: int) -> Records:
    return Records(
        data=pd.DataFrame([data]), start_year=year, gfactors=None, weights=None, adjust_ratios=None
    )


@lru_cache(maxsize=12)
def engine(year: int) -> Calculator:
    calc = Calculator(policy=Policy(), records=records({"RECID": 1, "MARS": 1}, year))
    calc.advance_to_year(year)
    return calc


def values(data: dict, year: int, outputs: tuple[str, ...]) -> dict[str, float]:
    """Fresh Records runs package validation and rebuilds derived input fields.

    Replace read AND calculated arrays, including filing-unit size, random credit
    draws and all default zeros. Reusing only mapped fields would leave stale
    state across households. No private Calculator attributes are changed.
    """
    fresh = records(data, year)
    with LOCK:
        calc = engine(year)
        for name in fresh.USABLE_READ_VARS | fresh.CALCULATED_VARS:
            calc.array(name, getattr(fresh, name).copy())
        calc.calc_all(zero_out_calc_vars=True)
        return {name: float(calc.array(name)[0]) for name in outputs}
