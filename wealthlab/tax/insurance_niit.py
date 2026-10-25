"""Reuse the pinned NIIT kernel for separately identified taxable policy income.

The full return already includes policy income on1040line5. A temporary interest
carrier is used ONLY in this isolated NIIT call, never for AGI, EIC, QBI, payroll,
credits or retirement income eligibility. Existing ordinary pensions stay outside
NII. No investment-expense or foreign-income adjustment is introduced here.
"""

from functools import lru_cache

from taxcalc import Policy
from taxcalc.calcfunctions import NetInvIncTax


@lru_cache(maxsize=12)
def policy(year):
    result = Policy()
    result.set_year(year)
    return result


def include(fresh, calc, year, amount, result):
    if not amount:
        return result
    fresh.e00300 += amount
    fresh.c00100[:] = calc.array("c00100")
    fresh.c01000[:] = calc.array("c01000")
    NetInvIncTax(policy(year), fresh)
    adjusted = float(fresh.niit[0])
    delta = adjusted - float(calc.array("niit")[0])
    # NIIT enters1040 total after credits; it cannot change earned-income credits.
    for key in ("niit", "c09200", "iitax"):
        if key in result:
            result[key] += delta
    return result
