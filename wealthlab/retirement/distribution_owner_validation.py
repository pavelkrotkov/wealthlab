"""Opening basis and conversion history describe prior years, not future receipts."""

from wealthlab.tax.projection_example import age


def validate_owners(case):
    for person in case.owners:
        validate_owner(person, case.year)


def validate_owner(person, year):
    if not 18 <= year - person.birth_date.year <= 120:
        raise ValueError("Distribution owners must be age 18 through 120 in the modeled year.")
    years = [entry.year for entry in person.conversions]
    if any(value >= year for value in years) or len(years) != len(set(years)):
        raise ValueError("Opening conversion history needs distinct years before the case year.")
    validate_roth_history(person, year, years)


def validate_roth_history(person, year, years):
    """The qualified-distribution clock and each conversion clock are distinct.

    A missing first Roth year is not interpreted as a completed five-year period.
    A conversion dated before that first contribution would contradict the pool.
    """
    first = person.roth_first_year
    if first is None:
        if person.roth_regular_basis or person.conversions or person.nj_roth_basis:
            raise ValueError("Roth basis requires the owner's first Roth contribution tax year.")
    else:
        if not person.birth_date.year <= first <= year:
            raise ValueError("First Roth year must be between birth and the modeled year.")
        if any(value < first for value in years):
            raise ValueError("A conversion cannot precede the first Roth contribution year.")


def validate_tax(case):
    annual = case.annual_tax_case
    if annual is None:
        return
    if annual.policy.year != case.year:
        raise ValueError("Annual tax forecast must match the distribution year.")
    expected = 2 if annual.filing.status == "joint" else 1
    if len(case.owners) != expected:
        raise ValueError("Tax filing unit must include all distribution owners in filing order.")
    validate_tax_ages(case, annual.filing, True)
    validate_tax_ages(case, annual.nj_filing or annual.filing, False)


def validate_tax_ages(case, filing, federal):
    ages = [age(person.birth_date, case.year, federal=federal) for person in case.owners]
    declared = [filing.age_primary, filing.age_spouse][: len(case.owners)]
    if ages != declared:
        raise ValueError("Tax forecast federal/NJ ages disagree with owner birth dates.")
