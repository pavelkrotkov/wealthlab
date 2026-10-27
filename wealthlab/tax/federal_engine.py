"""Reuse expensive policy initialization while replacing every household record array."""

from functools import lru_cache
from threading import RLock

import pandas as pd
from taxcalc import Calculator, Policy, Records

from wealthlab.tax.insurance_niit import include

# ponytail: one local-process lock; batch records if simulations need parallel throughput.
LOCK = RLock()


def records(data: dict, year: int) -> Records:
    return Records(
        data=pd.DataFrame([data]), start_year=year, gfactors=None, weights=None, adjust_ratios=None
    )


@lru_cache(maxsize=12)
def engine(year: int) -> Calculator:
    # e00800 is a numerical ordinary/noninvestment carrier, not an alimony fact.
    # No alimony input is supported; explicit inclusion avoids the statutory zero.
    policy = Policy()
    policy.implement_reform({"AlimonyReceived_frac_in_AGI": {year: 1.0}}, print_warnings=False)
    calc = Calculator(policy=policy, records=records({"RECID": 1, "MARS": 1}, year))
    calc.advance_to_year(year)
    return calc


def values(
    data: dict, year: int, outputs: tuple[str, ...], insurance_niit: float = 0
) -> dict[str, float]:
    """Return a fresh result dictionary for the complete immutable numerical input.

    The bounded process-local cache retains no scenario files. Every field,
    package year, requested output and explicit NIIT adjustment owns the key;
    changed inputs still go through the original fresh-record validation path.
    """
    return dict(cached_values(tuple(sorted(data.items())), year, outputs, insurance_niit))


@lru_cache(maxsize=4096)
def cached_values(items, year, outputs, insurance_niit):
    """Fresh Records runs package validation and rebuilds derived input fields.

    Replace read AND calculated arrays, including filing-unit size, random credit
    draws and all default zeros. Reusing only mapped fields would leave stale
    state across households. No private Calculator attributes are changed.
    """
    fresh = records(dict(items), year)
    with LOCK:
        calc = engine(year)
        for name in fresh.USABLE_READ_VARS | fresh.CALCULATED_VARS:
            calc.array(name, getattr(fresh, name).copy())
        calc.calc_all(zero_out_calc_vars=True)
        result = {name: float(calc.array(name)[0]) for name in outputs}
        return tuple(include(fresh, calc, year, insurance_niit, result).items())
