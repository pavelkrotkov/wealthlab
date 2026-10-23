"""Optional Owl benchmark in a deliberately simple, representable retirement case."""

from datetime import date


def cases() -> list[tuple[str, float, float]]:
    import owlplanner as owl

    # Fix age instead of letting this verification case expire as calendar years pass.
    birth = f"{date.today().year - 70}-01-01"
    plan = owl.Plan(["Synthetic"], [birth], [80], "Cash conservation", verbose=False)
    plan.setAccountBalances(taxable=[120], taxDeferred=[0], taxFree=[0], startDate="01-01")
    plan.setRates("user", values=[0, 0, 0, 0])
    plan.setAllocationRatios("spouses", generic=[[0, 0, 0, 100], [0, 0, 0, 100]])
    plan.setSpendingProfile("flat")
    plan.solve("maxSpending", {"solver": "HiGHS", "bequest": 0, "withMedicare": "none"})
    if plan.caseStatus != "solved":
        raise RuntimeError(f"Owl did not solve: {plan.caseStatus}")
    return [("Zero-return retirement cash conservation", float(plan.basis), 120_000 / plan.N_n)]
