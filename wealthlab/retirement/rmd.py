"""Use Owl's pinned IRS table data with explicit scenario year and beneficiary choice."""

from datetime import date
from decimal import ROUND_CEILING, Decimal


def start_age(person):
    if person.birth_date.year == 1959:
        if person.birth_1959_start_age is None:
            raise ValueError(
                "Born in 1959: explicitly choose the conditional RMD start age (73/75)."
            )
        return person.birth_1959_start_age
    if person.birth_date < date(1949, 7, 1):
        return Decimal("70.5")
    if person.birth_date.year <= 1950:
        return 72
    return 73 if person.birth_date.year <= 1959 else 75


def divisor(person, year):
    age = year - person.birth_date.year
    earliest = 72 if person.birth_date.year <= 1950 else 73
    if age < earliest:
        return None
    if age < start_age(person):
        return None
    try:
        from owlplanner.data.irs_590b import JOINT_LIFE_TABLE, UNIFORM_LIFETIME_DIVISOR_BY_AGE
    except ImportError as error:
        raise ValueError(
            "Install the benchmarks extra to enable the pinned Owl RMD tables."
        ) from error
    if person.rmd_table == "uniform":
        return Decimal(str(UNIFORM_LIFETIME_DIVISOR_BY_AGE[age]))
    return joint_divisor(person, year, JOINT_LIFE_TABLE)


def joint_divisor(person, year, table):
    spouse = person.spouse_birth_date
    if spouse is None or spouse.year - person.birth_date.year <= 10:
        raise ValueError(
            "Joint RMD table requires an explicitly sole spouse over ten years younger."
        )
    spouse_age = year - spouse.year
    if not 20 <= spouse_age <= 120:
        raise ValueError("The pinned joint table supports spouse ages 20 through 120.")
    return Decimal(str(table[year - person.birth_date.year][spouse_age]))


def requirements(case):
    """Opening balances mean prior December 31 values in this annual layer.

    Round required withdrawals upward to cents so rounding cannot leave a small
    gap. The schedule targets December 31 even in the first RMD year; April
    first-year deferral and prior-year arrears need the later household layer.
    """
    result = {}
    for person in case.owners:
        value = sum(
            account.balance
            for account in case.accounts
            if account.owner == person.id and account.wrapper == "traditional"
        )
        factor = divisor(person, case.year)
        required = Decimal(0)
        if factor is not None:
            required = (value / factor).quantize(Decimal(".01"), rounding=ROUND_CEILING)
        result[person.id] = dict(required=required, withdrawn=Decimal(0), divisor=factor)
    return result
