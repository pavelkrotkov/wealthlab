"""Validate full-month enrollment and unambiguous income before premium funding.

Each history record represents one tax return shared by its listed members.
Overlapping records for the same person/year are rejected, so neither spouse's
MAGI can be accidentally selected from a second conflicting return. Explicit
SSA determinations also have one owner and one premium year.
"""

from datetime import date
from itertools import chain

from wealthlab.retirement.medicare_enrollment import (
    validate_coverage,
    validate_income_coverage,
    validate_overlaps,
)
from wealthlab.retirement.medicare_history import validate_determination


def validate(case):
    if not case.complete_context:
        raise ValueError("Confirm Medicare coverage, return history and premium assumptions.")
    if not 0 < case.end_year - case.start_year <= 120:
        raise ValueError("Medicare projection must span one to 120 whole calendar years.")
    if case.future_policy == "freeze_2026" and (case.premium_growth or case.threshold_growth):
        raise ValueError("Frozen Medicare policy requires zero premium and threshold growth.")
    validate_records(case)
    members = {m.id for m in case.members}
    for coverage in case.coverage:
        validate_coverage(case, coverage, members)
    validate_overlaps(case)
    validate_history(case, members)
    validate_income_coverage(case)


def validate_records(case):
    groups = [case.members, case.coverage, case.income_history, case.determinations, case.receipts]
    records = list(chain.from_iterable(groups))
    ids = [item.id for item in records]
    if len(ids) != len(set(ids)) or any(item.provenance == "unresolved" for item in records):
        raise ValueError("Medicare IDs must be unique and critical assumptions resolved.")
    start, end = date(case.start_year, 1, 1), date(case.end_year, 1, 1)
    if any(not start <= item.date < end for item in case.receipts):
        raise ValueError("Medicare cash receipts must fall within the projection.")


def validate_history(case, members):
    keys = []
    for income in case.income_history:
        if income.filing != "joint" and len(income.members) != 1:
            raise ValueError("Only a joint return can supply income for two Medicare members.")
        if len(income.members) != len(set(income.members)) or set(income.members) - members:
            raise ValueError("Income record members must be known and distinct.")
        keys.extend((member, income.year) for member in income.members)
    if len(keys) != len(set(keys)):
        raise ValueError("Supply one income return per Medicare member and tax year.")
    validate_determinations(case)


def validate_determinations(case):
    keys = [(d.member, d.premium_year) for d in case.determinations]
    if len(keys) != len(set(keys)):
        raise ValueError("Supply one Medicare determination per member and premium year.")
    incomes = {i.id: i for i in case.income_history}
    for item in case.determinations:
        validate_determination(case, item, incomes)
