"""Verify 2025 federal tax and employee payroll mappings with synthetic cases."""

import pandas as pd
from taxcalc import Calculator, Policy, Records


def calculate(wages: float, gains: float) -> dict[str, float]:
    """Two under-65 joint filers, no dependents or deductions beyond the standard one."""
    data = pd.DataFrame(
        [
            {
                "RECID": 1,
                "MARS": 2,
                "XTOT": 2,
                "age_head": 40,
                "age_spouse": 40,
                "e00200": wages,
                "e00200p": wages,
                "p23250": gains,
            }
        ]
    )
    records = Records(data=data, start_year=2025, gfactors=None, weights=None, adjust_ratios=None)
    calc = Calculator(policy=Policy(), records=records)
    calc.advance_to_year(2025)
    calc.calc_all()
    return {key: float(calc.array(key)[0]) for key in ("iitax", "ptax_was", "ptax_amc")}


def cases() -> list[tuple[str, float, float]]:
    """The payroll model includes both employer and employee regular wage taxes."""
    wage = calculate(150_000, 0)
    capital = calculate(0, 150_000)
    employee = wage["ptax_was"] / 2 + wage["ptax_amc"]
    return [
        ("2025 joint wage income tax", wage["iitax"], 15_898.0),
        ("2025 employee payroll tax", employee, 11_475.0),
        ("2025 joint long-term gain tax", capital["iitax"], 3_270.0),
    ]
