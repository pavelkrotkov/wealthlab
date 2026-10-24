"""Keep the regular death PIA, hypothetical life benefit and inherited delayed credits distinct."""

from decimal import Decimal

from wealthlab.retirement.social_amounts import dime, pia, project_pia, reduced
from wealthlab.retirement.social_dates import distance, seventieth_month, shift


def original(case, worker, month, fra):
    """The deemed PIA can exceed regular death PIA; an early claim limit is separate.

    All pre-claim delayed credits through the month before death are available
    to the survivor, even if the worker's current-year credits were not yet paid.
    The no-suspension/no-work-deduction history remains an explicit condition.
    """
    death_month = shift(worker.death_date, 0)
    life_pia = pia(worker, month, case.future_cola_assumption)
    death_pia = life_pia
    if worker.survivor_pia_january_2026 is not None:
        death_pia = project_pia(
            worker.survivor_pia_january_2026, month, case.future_cola_assumption
        )
    actually_claimed = worker.own_insured and worker.claim_month < death_month
    early = max(0, distance(worker.claim_month, fra)) if actually_claimed else 0
    life_benefit = reduced(life_pia, early)
    end = min(worker.claim_month, death_month, seventieth_month(worker.birth_date))
    credits = max(0, distance(fra, end))
    inherited = dime(life_pia * credits / 150)
    deemed_pia = max(death_pia, life_benefit + inherited) if inherited else death_pia
    limit = None
    if actually_claimed and early:
        limit = max(dime(death_pia * Decimal(".825")), life_benefit)
    return dict(
        death_pia=death_pia,
        inherited_delayed_credits=inherited,
        deemed_pia=deemed_pia,
        reduced_worker_limit=limit,
    )
