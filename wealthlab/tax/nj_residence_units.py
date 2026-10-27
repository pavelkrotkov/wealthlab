"""Explicit spouse exceptions determine return units without changing each person's status."""

from wealthlab.tax.filing import Filing
from wealthlab.tax.nj_residence_calendar import resident_days
from wealthlab.tax.nj_residence_income import sourced_nonpension


def units(profile, filing, year):
    """Keep federal joint identity while supporting the specific NJ spouse exceptions.

    Common residence periods may follow federal joint filing. Different dates
    do not automatically split a joint return: only the expressly selected
    mixed-residence or sole-NJ-source full-nonresident exception is supported.
    """
    people = sorted(profile.people, key=lambda p: p.role != "primary")
    days = {p.id: resident_days(p, year) for p in people}
    if filing.status != "joint":
        if len(people) != 1 or profile.filing_election != "follow_federal":
            raise ValueError(
                "A nonjoint filing unit needs one person and its matching NJ filing status."
            )
        return [unit([people[0].id], filing, days[people[0].id])]
    if len(people) != 2:
        raise ValueError("A joint filing unit requires two stable people.")
    return joint_units(profile, filing, people, days)


def joint_units(profile, filing, people, days):
    left, right = (days[p.id] for p in people)
    if profile.filing_election == "follow_federal":
        if left != right:
            raise ValueError(
                "Different spouse NJ periods require an explicitly supported filing election."
            )
        return [unit([p.id for p in people], filing, left)]
    validate_separate(profile, people, days)
    ages = [filing.age_primary, filing.age_spouse]
    return [
        unit(
            [p.id],
            Filing(status="separate", age_primary=age, age_spouse=0, dependents=[]),
            days[p.id],
        )
        for p, age in zip(people, ages, strict=True)
    ]


def validate_separate(profile, people, days):
    if not profile.filing_election_assumed_confirmed:
        raise ValueError("Confirm the applicable NJ separate-return spouse exception.")
    resident = [bool(days[p.id]) for p in people]
    if profile.filing_election == "mixed_spouse_separate" and sum(resident) == 1:
        return
    if one_nonresident_source(profile, people, resident):
        return
    raise ValueError(
        "The supplied spouses do not meet this supported NJ separate-return exception."
    )


def source_income(profile, owner):
    # A sourced loss does not establish the other spouse's lack of NJ activity.
    return any(
        r.amount != 0 for r in profile.income if r.owner_id == owner and sourced_nonpension(r)
    )


def unit(owners, filing, days):
    return dict(owners=owners, filing=filing, days=days)


def one_nonresident_source(profile, people, resident):
    if profile.filing_election != "one_nonresident_source_separate" or any(resident):
        return False
    return sum(source_income(profile, p.id) > 0 for p in people) == 1
