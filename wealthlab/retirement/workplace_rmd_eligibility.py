"""One plan's owner, beneficiary table and cash-access dates determine RMD eligibility.

Table eligibility is supplied rather than inferred from marriage. Qualified
plan cash access still requires confirmed separation before December catch-up;
there is no inferred current-employer exception or first-year deadline deferral.
"""

from datetime import date
from types import SimpleNamespace

from wealthlab.retirement.rmd import divisor


def owner_context(group, cash, accounts, members):
    owner = accounts[group.sources[0]].owner
    profile = cash.profiles[group.sources[0]]
    return SimpleNamespace(
        birth_date=members[owner].birth_date,
        birth_1959_start_age=profile.birth_1959_start_age,
        rmd_table=group.rmd_table,
        spouse_birth_date=group.spouse_birth_date,
    )


def validate_group(group, cash, scenario):
    if not (
        group.complete_distinct_plan_balances_and_distributions_confirmed
        and group.beneficiary_table_eligibility_confirmed
    ):
        raise ValueError("Confirm complete distinct-plan RMD balances and beneficiary eligibility.")
    accounts = {a.id: a for a in scenario.accounts}
    members = {m.id: m for m in scenario.members}
    validate_sources(group, cash, accounts)
    person = owner_context(group, cash, accounts, members)
    validate_table(group, person, members)
    validate_deadlines(person, group, cash, scenario)


def validate_table(group, person, members):
    if group.rmd_table == "uniform":
        if group.spouse_birth_date is not None:
            raise ValueError("Uniform RMD table does not accept a sole-younger-spouse date.")
        return
    others = {m.birth_date for m in members.values() if m.birth_date != person.birth_date}
    spouse = group.spouse_birth_date
    if spouse not in others or spouse is None or spouse.year - person.birth_date.year <= 10:
        raise ValueError("Joint RMD table requires the actual sole spouse over ten years younger.")


def validate_sources(group, cash, accounts):
    if len({accounts[s].owner for s in group.sources}) != 1:
        raise ValueError("An RMD plan group must have one owner.")
    choices = {cash.profiles[s].birth_1959_start_age for s in group.sources}
    if len(choices) != 1:
        raise ValueError("One plan cannot have conflicting RMD start-age assumptions.")


def validate_deadlines(person, group, cash, scenario):
    for year in range(scenario.start.year, scenario.end.year):
        factor = divisor(person, year)
        if factor is not None and any(
            cash.profiles[s].separation_date > date(year, 12, 1) for s in group.sources
        ):
            raise ValueError("This RMD cash profile requires source separation by December 1.")
