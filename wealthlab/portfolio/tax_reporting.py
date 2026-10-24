"""Matched annual liability comparisons preserve separate scenario carryforward paths.

Baseline forecasts exclude modeled disposals and distributions. Each path carries
its own prior capital results into later years; ordinary dividend income cannot
be netted directly with capital losses. Decision-date calls pass an observation
date so future dividend holding days cannot improve a current tax budget."""

from wealthlab.portfolio.distribution_tax import include, income
from wealthlab.portfolio.loss_attribution import allocate
from wealthlab.portfolio.tax_recognition import gains, with_carry, with_gains
from wealthlab.tax.annual import evaluate


def validate_tax_cases(case):
    if not case.lot_tax_cases:
        if any(policy.mode == "tax_budget" for policy in case.sale_policies):
            raise ValueError("Tax-budget policies require annual lot_tax_cases forecasts.")
        return
    if not case.federal_wash_tracking or case.nj_wash_treatment == "unconfirmed":
        raise ValueError(
            "Lot tax comparison requires federal wash tracking and an explicit NJ treatment."
        )
    years = [item.policy.year for item in case.lot_tax_cases]
    if years != list(range(case.as_of.year, case.end.year + 1)):
        raise ValueError("Supply one ordered annual tax case for every projection calendar year.")
    validate_later_carries(case.lot_tax_cases)


def validate_later_carries(cases):
    for item in cases[1:]:
        if item.federal_income.short_carry or item.federal_income.long_carry:
            raise ValueError(
                "Enter opening capital carry only in the first year; later carries are computed."
            )


def report(case, book, through_year=None, as_of=None):
    previous_with = previous_without = None
    results = []
    for annual in case.lot_tax_cases:
        if through_year is not None and annual.policy.year > through_year:
            break
        federal, nj, pending = gains(book, annual.policy.year)
        baseline = with_carry(annual, previous_without)
        opening = with_carry(annual, previous_with)
        modeled = with_gains(opening, federal, nj)
        dist_fed, dist_nj, qualification_pending = income(
            case, book, annual.policy.year, as_of or case.end
        )
        modeled = include(modeled, dist_fed, dist_nj)
        previous_without = evaluate(baseline)
        previous_with = evaluate(modeled)
        results.append(
            dict(
                year=annual.policy.year,
                federal_loss_use=allocate(opening, book, dist_fed, previous_with),
                distribution_federal=dist_fed,
                distribution_nj=dist_nj,
                qualification_pending=qualification_pending,
                recognized_federal=federal,
                recognized_nj=nj,
                pending_losses=pending,
                without_lot_trades=previous_without,
                with_lot_trades=previous_with,
                incremental_liability=previous_with["total_liability"]
                - previous_without["total_liability"],
            )
        )
    return results
