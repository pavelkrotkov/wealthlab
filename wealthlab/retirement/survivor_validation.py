"""Dated survivor assumptions require explicit eligibility and a usable regular death PIA."""

from datetime import date

from wealthlab.retirement.social_amounts import dime
from wealthlab.retirement.social_dates import earliest_survivor_month, shift


def validate_mortality(case, members):
    end = date(case.end_year, 1, 1)
    for person in case.members:
        validate_death(person, case.survival_policy, end)
        validate_required_date(person, members.get(person.partner), end)
        validate_claim(person, members)


def validate_death(person, policy, end):
    if person.death_date is not None:
        if person.death_date < person.birth_date:
            raise ValueError("Death cannot precede birth.")
        if person.death_date < end and policy == "all_members_survive_projection":
            raise ValueError(
                "Use dated-deaths survival policy for a death within/before the projection."
            )
    override = person.survivor_pia_january_2026
    if override is not None and dime(override) != override:
        raise ValueError("A supplied regular survivor PIA must be a dime multiple.")


def validate_claim(person, members):
    if person.survivor_claim_month is None:
        return
    worker = members.get(person.partner)
    if worker is None or worker.death_date is None:
        raise ValueError("A survivor claim requires a known partner and dated death.")
    start = max(earliest_survivor_month(person.birth_date), shift(worker.death_date, 0))
    if person.survivor_claim_month.day != 1 or person.survivor_claim_month < start:
        raise ValueError(
            "Survivor claim must be an eligible first-of-month at/after age60 and death."
        )
    if person.death_date is not None and person.survivor_claim_month >= shift(person.death_date, 0):
        raise ValueError("A survivor cannot start benefits in or after their own death month.")
    validate_survivor_pia(person, worker)


def validate_death_pia(worker):
    """Conservatively require supplied PIA through the worker's age62 calendar year.

    Windex/alternate survivor PIA is not derived here. This calendar-year guard
    is deliberately broader than the legal before-age62 test; it avoids silently
    substituting an ordinary retirement PIA around an unvalidated boundary.
    """
    override = worker.survivor_pia_january_2026
    if worker.death_date.year <= worker.birth_date.year + 62 and override is None:
        raise ValueError(
            "Supply a survivor PIA for death in/before the worker's age62 calendar year."
        )
    if not worker.pia_january_2026 and not override:
        raise ValueError("Confirmed survivor eligibility needs a positive supplied death PIA.")


def validate_survivor_pia(person, worker):
    if person.survivor_eligibility_confirmed:
        validate_death_pia(worker)


def validate_required_date(person, worker, end):
    if not person.survivor_eligibility_confirmed or person.survivor_claim_month is not None:
        return
    if worker is None or worker.death_date is None:
        return
    if worker.death_date < end:
        raise ValueError(
            "Supply a survivor entitlement month for confirmed in-horizon eligibility."
        )
