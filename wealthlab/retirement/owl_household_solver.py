"""Reuse one optional OWL solve; preserve its policy and forecasts before native replay."""

from importlib.metadata import version

import numpy as np


def solve(case):
    try:
        import owlplanner as owl
    except ImportError as error:
        raise ValueError("Install the benchmarks extra to enable the OWL comparison.") from error

    born = f"{case.start_year - case.age}-07-01"
    plan = owl.Plan(
        ["Reference"], [born], [case.age + case.years - 1], "Household reference", verbose=False
    )
    plan.setAccountBalances(
        taxable=[float(case.cash)],
        taxDeferred=[float(case.traditional_ira)],
        taxFree=[float(case.roth_ira)],
        units="1",
        startDate="01-01",
    )
    # All four asset returns and the inflation series are zero. Cash has no
    # appreciation or yield, so neither taxable sales nor yield basis is inferred.
    plan.setRates("user", values=[0, 0, 0, 0])
    plan.setAllocationRatios("spouses", generic=[[0, 0, 0, 100], [0, 0, 0, 100]])
    plan.setSpendingProfile("flat")
    plan.setHeirsTaxRate(float(case.heirs_tax_rate * 100))
    plan.solve(
        "maxBequest",
        dict(
            solver="HiGHS",
            netSpending=float(case.annual_spending),
            units="1",
            maxRothConversion=0,
            withMedicare="none",
        ),
    )
    if plan.caseStatus != "solved":
        raise ValueError(f"OWL reference did not solve: {plan.caseStatus}.")
    validate(plan, case)
    return dict(
        version=version("owlplanner"),
        years=plan.year_n.tolist(),
        withdrawals=plan.w_ijn.tolist(),
        balances=plan.b_ijn.tolist(),
        conversions=plan.x_in.tolist(),
        cash_deposits=plan.d_in.tolist(),
        spending=plan.g_n.tolist(),
        federal_tax=plan.T_n.tolist(),
        state_tax=plan.st_T_n.tolist(),
        deduction=plan.sigmaBar_n.tolist(),
        agi=plan.MAGI_n.tolist(),
        inflation=plan.gamma_n.tolist(),
        estate_proxy=plan.bequest,
        heirs_tax_rate=str(case.heirs_tax_rate),
        assumed_obbba_replacement_year=int(plan.yOBBBA),
    )


def validate(plan, case):
    if plan.year_n.tolist() != list(range(case.start_year, case.start_year + case.years)):
        raise ValueError("OWL reference years differ from the declared case; dates cannot shift.")
    arrays = [
        plan.w_ijn,
        plan.b_ijn,
        plan.g_n,
        plan.T_n,
        plan.st_T_n,
        plan.x_in,
        plan.sigmaBar_n,
        plan.MAGI_n,
        plan.gamma_n,
    ]
    if not all(np.isfinite(a).all() for a in arrays):
        raise ValueError("OWL reference returned nonfinite results.")
    if plan.w_ijn.shape != (1, 4, case.years) or plan.b_ijn.shape != (1, 4, case.years + 1):
        raise ValueError("OWL reference account axes differ from this supported profile.")
    if np.any(np.abs(plan.x_in) > 0.000001) or np.any(np.abs(plan.st_T_n) > 0.000001):
        raise ValueError("This reference locks conversions and omits state taxes explicitly.")
