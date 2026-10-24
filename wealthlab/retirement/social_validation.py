"""Reject ambiguous histories instead of silently omitting work or entitlement rules.

This first claim layer assumes survival and no work-test deduction, disability,
voluntary suspension or restricted-application history. Those are explicit case
conditions, not deductions inferred from the employment ledger. Integration
must verify them again when wages or claim policies change. Uninsured persons
can receive a confirmed spouse benefit but cannot carry a positive own PIA.
PIA is an SSA dime amount, distinct from an estimated rounded monthly check.
"""

from datetime import date

from wealthlab.retirement.social_amounts import dime
from wealthlab.retirement.social_dates import earliest_retirement_month


def validate(case):
    if not 0 < case.end_year - case.start_year <= 120:
        raise ValueError("Social Security projection must span one to 120 calendar years.")
    if not case.no_earnings_test_deductions_confirmed:
        raise ValueError("The ordinary-claim layer requires no earnings-test deductions.")
    if not case.no_other_auxiliaries_confirmed:
        raise ValueError(
            "This claim layer requires no other record auxiliaries/family-maximum claims."
        )
    members = {person.id: person for person in case.members}
    if len(members) != len(case.members):
        raise ValueError("Social Security member IDs must be unique.")
    for person in case.members:
        validate_person(person, case)
        validate_partner(person, members)
    from wealthlab.retirement.survivor_validation import validate_mortality

    validate_mortality(case, members)


def validate_person(person, case):
    if person.provenance == "unresolved":
        raise ValueError("Resolve critical Social Security assumptions before calculating.")
    if not date(1943, 1, 2) <= person.birth_date < date(case.start_year, 1, 1):
        raise ValueError("Use births after January 1, 1943 and before the projection start.")
    if person.claim_month.day != 1 or person.claim_month < earliest_retirement_month(
        person.birth_date
    ):
        raise ValueError(
            "Own/spouse claim month must be a first-of-month date at or after eligibility."
        )
    if not person.own_insured and person.pia_january_2026:
        raise ValueError("An uninsured owner cannot have a positive retirement PIA.")
    if dime(person.pia_january_2026) != person.pia_january_2026:
        raise ValueError(
            "Supply the SSA PIA as a dime multiple, not an unrounded benefit estimate."
        )


def validate_partner(person, members):
    if person.partner is None:
        if person.spousal_eligibility_confirmed:
            raise ValueError("Spousal eligibility requires a configured partner.")
        return
    partner = members.get(person.partner)
    if partner is None or partner.id == person.id or partner.partner != person.id:
        raise ValueError("Social Security partner references must be distinct and reciprocal.")
    if person.spousal_eligibility_confirmed and not partner.own_insured:
        raise ValueError("A spousal benefit requires the partner's insured worker record.")
