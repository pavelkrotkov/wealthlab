"""Retirement and dependent employer contracts are one atomic sourced decision.

Fixed former-employer rights need an explicit independent source. Otherwise each
choice supplies a complete native work/compensation profile for its exact dates;
an early salary cutoff cannot silently retain the later profile's vesting.
"""

from datetime import date

from wealthlab.optimization import employment_profiles as profiles


def validate(case):
    offered = index_profiles(case)
    if not configured(case, offered):
        return
    for offer in offered.values():
        profiles.validate_offer(case, offer)
    if offered:
        profiles.baseline(case, offered)
    for dimension in case.dimensions:
        for choice in dimension.choices:
            validate_choice(case, choice, offered)


def configured(case, offered):
    independence = case.employer_independence
    if case.household.compensation_plan is None:
        if any((independence, offered, declared(case))):
            raise ValueError("Employer applicability requires an original compensation plan.")
        return False
    if independence:
        validate_independence(case, independence, offered)
    elif not offered:
        raise ValueError("Supply employer independence or complete matching employment offers.")
    return True


def validate_independence(case, record, offered):
    profiles.source(record, case.household)
    original = case.household.compensation_plan
    expected = {t.id for t in original.tranches}
    if (
        len(record.tranche_ids) != len(set(record.tranche_ids))
        or set(record.tranche_ids) != expected
    ):
        raise ValueError("Employer independence must explicitly cover every original tranche once.")
    if not record.independent_of_all_candidate_employment_and_retirement_confirmed:
        raise ValueError("Confirm employer rights are independent of every candidate work choice.")
    if offered:
        raise ValueError("Choose either fixed employer independence or matched employment offers.")


def validate_choice(case, choice, offered):
    if choice.employment_offer is None:
        if offered and choice.retirement_dates:
            raise ValueError(
                "Retirement choices must select their matching employment offer atomically."
            )
        return
    offer = offered.get(choice.employment_offer)
    if offer is None:
        raise ValueError("Every employment choice must name a supplied complete profile.")
    if choice.retirement_dates != offer.retirement_dates:
        raise ValueError("Employment choices must match every source-profile retirement date.")


def apply(data, case, selection):
    identity = selected(selection)
    if identity is None:
        if case.employment_offers and current_dates(data) != profiles.dates(case.household):
            raise ValueError("Changed retirement dates require a matching employment profile.")
        return
    offer = {o.id: o for o in case.employment_offers}.get(identity)
    if offer is None or current_dates(data) != offer.retirement_dates:
        raise ValueError("Candidate retirement dates do not match the supplied employment profile.")
    data["employment_plan"] = (
        offer.employment_plan.model_dump(mode="json") if offer.employment_plan else None
    )
    data["compensation_plan"] = offer.compensation_plan.model_dump(mode="json")


def current_dates(data):
    return {
        member["id"]: date.fromisoformat(member["retirement_date"]) for member in data["members"]
    }


def declared(case):
    return any(c.employment_offer for d in case.dimensions for c in d.choices)


def selected(selection):
    named = [choice.employment_offer for choice in selection if choice.employment_offer is not None]
    if len(named) > 1:
        raise ValueError("Only one dimension can select a complete employment profile.")
    return named[0] if named else None


def index_profiles(case):
    offered = {offer.id: offer for offer in case.employment_offers}
    if len(offered) != len(case.employment_offers):
        raise ValueError("Employment offer IDs must be unique.")
    maps = [tuple(sorted(offer.retirement_dates.items())) for offer in offered.values()]
    if len(set(maps)) != len(maps):
        raise ValueError("Supply one unambiguous employer profile for each retirement-date map.")
    return offered
