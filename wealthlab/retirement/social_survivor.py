"""Age-reduce widow(er) entitlement before applying the deceased worker's RIB limit."""

from decimal import Decimal, localcontext
from fractions import Fraction

from wealthlab.retirement.social_amounts import dime
from wealthlab.retirement.social_dates import (
    alive,
    distance,
    earliest_survivor_month,
    full_retirement_month,
    shift,
)
from wealthlab.retirement.survivor_basis import original


def amount(case, person, month, members, fras, own):
    worker = members.get(person.partner)
    if not eligible(person, worker, month):
        return dict(
            survivor_original=Decimal(0),
            survivor_after_age_reduction=Decimal(0),
            survivor_worker_limit=None,
            survivor_before_own_offset=Decimal(0),
            survivor_excess=Decimal(0),
            inherited_delayed_credits=Decimal(0),
        )
    basis = original(case, worker, month, fras[worker.id])
    fra = full_retirement_month(person.birth_date, survivor=True)
    early = max(0, distance(person.survivor_claim_month, fra))
    maximum = distance(earliest_survivor_month(person.birth_date), fra)
    aged = age_reduce(basis["deemed_pia"], early, maximum)
    limited = aged
    if basis["reduced_worker_limit"] is not None:
        limited = min(limited, basis["reduced_worker_limit"])
    return dict(
        survivor_original=basis["deemed_pia"],
        survivor_after_age_reduction=aged,
        survivor_worker_limit=basis["reduced_worker_limit"],
        survivor_before_own_offset=limited,
        survivor_excess=max(Decimal(0), limited - own),
        inherited_delayed_credits=basis["inherited_delayed_credits"],
    )


def eligible(person, worker, month):
    if not person.survivor_eligibility_confirmed or person.survivor_claim_month is None:
        return False
    if worker is None or worker.death_date is None:
        return False
    start = max(person.survivor_claim_month, shift(worker.death_date, 0))
    return alive(person, month) and month >= start


def age_reduce(amount, early, maximum):
    """CFR404.410(c): the maximum ordinary aged reduction is28.5 percent at60.

    Use actual age60/FRA attainment months, including a first-day birthday, and
    preserve the rational fraction until the final statutory dime truncation.
    """
    with localcontext() as context:
        context.prec = 50
        rate = Fraction(285 * early, 1000 * maximum)
        return dime(amount * (rate.denominator - rate.numerator) / rate.denominator)
