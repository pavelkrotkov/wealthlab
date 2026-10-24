"""Published 2025/2026 limits; no inferred future-law indexing or plan exceptions."""

from decimal import Decimal

LIMITS = {
    2025: dict(ira=7000, ira_catchup=1000, workplace=23500, catchup=7500, special=11250),
    2026: dict(ira=7500, ira_catchup=1100, workplace=24500, catchup=8000, special=11250),
}
IRA_SOURCE = "https://www.irs.gov/publications/p590a"
PLAN_SOURCE = "https://www.irs.gov/pub/irs-drop/n-25-67.pdf"


def age(person, year):
    return year - person.birth_date.year


def ira_limit(person, year):
    values = LIMITS[year]
    amount = values["ira"] + (values["ira_catchup"] if age(person, year) >= 50 else 0)
    return min(Decimal(amount), person.ira_compensation_budget)


def workplace_limits(person, year):
    values = LIMITS[year]
    extra = 0
    if person.catchup_permitted and age(person, year) >= 50:
        extra = values["special"] if 60 <= age(person, year) <= 63 else values["catchup"]
    total = min(Decimal(values["workplace"] + extra), person.workplace_compensation)
    pretax = total
    if year == 2026 and person.prior_employer_wages > 150000:
        pretax = min(pretax, Decimal(values["workplace"]))
    return (total, pretax) if person.workplace_eligible else (Decimal(0), Decimal(0))
