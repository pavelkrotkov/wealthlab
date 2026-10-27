"""Reuse only complete prepared PR policy identities; refresh all household arrays.

The policy is fully determined here by Tax-Calculator's installed law year,
the fixed ordinary-income reform and a restored exact STD vector on each call.
This cache never enters the ordinary federal result cache. The existing shared
lock and public Records/Calculator APIs retain the normal engine's reset rule.
"""

from decimal import Decimal
from functools import lru_cache

import numpy as np
from taxcalc import Calculator, Policy

from wealthlab.tax.federal_engine import LOCK, records


@lru_cache(maxsize=12)
def engine(year: int):
    policy = Policy()
    policy.set_year(year)
    policy.implement_reform(
        {"AlimonyReceived_frac_in_AGI": {year: 1.0}},
        print_warnings=False,
    )
    calc = Calculator(policy=policy, records=records({"RECID": 1, "MARS": 1}, year))
    calc.advance_to_year(year)
    return calc, tuple(calc.policy_param("STD"))


def values(data: dict, year: int, ratio: Decimal, outputs: tuple[str, ...]):
    fresh = records(data, year)
    with LOCK:
        calc, standard = engine(year)
        # The public setter expects the current-year x filing-status shape.
        # Always derive from the immutable original row, never the last ratio.
        calc.policy_param("STD", np.asarray([standard]) * float(ratio))
        for name in fresh.USABLE_READ_VARS | fresh.CALCULATED_VARS:
            calc.array(name, getattr(fresh, name).copy())
        calc.calc_all(zero_out_calc_vars=True)
        return {name: float(calc.array(name)[0]) for name in outputs}
