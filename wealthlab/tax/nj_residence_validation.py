"""Fail closed on unknown status, source identity and unsupported elections.

Income IDs belong to this person/year, not to a federal basis or an address.
A complete conditional residence calendar and independently confirmed filing
facts are prerequisites to any favorable nonresident result. US citizenship
is an explicit supported-profile condition, not a conclusion inferred from NJ.
"""

from datetime import date, timedelta

from wealthlab.tax.nj_residence_calendar import resident_days, validate_status


def validate(profile, filing, year):
    if not date(year, 1, 1) - timedelta(days=1) <= profile.as_of <= date(year, 12, 31):
        raise ValueError("NJ observation date must belong to this calendar tax year.")
    people = validate_identities(profile)
    validate_people(profile.people, year)
    for row in profile.income:
        validate_row(row, people, year)
    if not profile.filing_election_assumed_confirmed:
        raise ValueError("Confirm the NJ filing election independently of federal filing status.")
    if filing.dependents and profile.filing_election != "follow_federal":
        raise ValueError(
            "Separate NJ spouse exceptions need explicit dependent allocation support."
        )


def validate_row(row, people, year):
    if row.owner_id not in people or row.received.year != year:
        raise ValueError("NJ income needs an existing owner and the correct recognition year.")
    if not row.amount_and_classification_assumed_confirmed:
        raise ValueError("Confirm independent NJ income amount/basis and classification.")
    if row.kind != "dispositions" and row.amount < 0:
        raise ValueError("Only independently classified NJ dispositions accept signed amounts.")


def validate_people(people, year):
    for person in people:
        validate_status(person, resident_days(person, year), year)
        if not person.us_citizen_full_year_assumed_confirmed:
            raise ValueError("This profile requires confirmed full-year US citizen tax context.")


def validate_identities(profile):
    people = {p.id: p for p in profile.people}
    roles = [p.role for p in profile.people]
    if (
        len(people) != len(profile.people)
        or len(set(roles)) != len(roles)
        or "primary" not in roles
    ):
        raise ValueError("NJ residence requires unique stable people and filing roles.")
    if len(profile.income) != len({r.id for r in profile.income}):
        raise ValueError("NJ source-income IDs must be unique within the annual profile.")
    return people
