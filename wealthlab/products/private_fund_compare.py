"""Run the fund and an independently configured unlevered tax proxy through one household engine.

The same realized paths and household background preserve capital and spending
comparability. Marked wealth with outstanding interests/receivables is reported
as conditional wealth, never as a fully liquidated after-tax ranking.
"""

from wealthlab.markets.household_run import paired, run


def compare(fund, reference, batch, binding, indices=None):
    validate_matched(fund, reference)
    indices = None if indices is None else list(indices)
    left = run(fund, batch, binding, indices)
    right = run(reference, batch, binding, indices)
    return dict(
        fund=left,
        reference=right,
        differences=paired(right, left),
        batch=batch.export(),
        exit_status=[
            exit_status(a, b) for a, b in zip(left["details"], right["details"], strict=True)
        ],
    )


def validate_matched(fund, reference):
    excluded = {"name", "sleeve_plan"}
    if fund.model_dump(exclude=excluded) != reference.model_dump(exclude=excluded):
        raise ValueError(
            "Private-fund comparisons require identical household capital and background."
        )
    if not fund.sleeve_plan or not reference.sleeve_plan:
        raise ValueError("Both product policies require complete household sleeve plans.")
    if len(fund.sleeve_plan.sleeves) != 1 or len(reference.sleeve_plan.sleeves) != 1:
        raise ValueError("This comparison requires one complete product account per policy.")
    validate_profiles(fund, reference)
    validate_reference(reference.sleeve_plan.sleeves[0].case)


def validate_profiles(fund, reference):
    for scenario in (fund, reference):
        if scenario.sleeve_plan.sleeves[0].private_fund_contract is None:
            raise ValueError(
                "Confirm independent cash-distribution tax profiles for both policies."
            )


def validate_reference(case):
    if case.short_multiple or case.long_multiple > 1 or case.maintenance_fraction_of_gross != 1:
        raise ValueError("The unlevered reference requires no shorts and 100% gross maintenance.")


def exit_status(fund, reference):
    return dict(
        path=fund["path"],
        fund_complete=completed(fund),
        reference_complete=completed(reference),
        both_fully_cash_liquidated=completed(fund) and completed(reference),
    )


def completed(detail):
    return detail["rows"][-1]["sleeve_audit"][-1].get("fund_complete_liquidation", False)
