"""IRA phaseouts preserve the distinction between permission and deductibility."""

from decimal import ROUND_CEILING, Decimal

from wealthlab.retirement.contribution_assumptions import rule_year
from wealthlab.retirement.contribution_rules import LIMITS, age


def spouse_covered(case, person):
    return case.spouse_covered_by_workplace_plan or any(
        p.id != person.id and p.covered_by_workplace_plan for p in case.contributors
    )


def phaseout(case, person, roth):
    if case.filing == "separate" and case.lived_with_spouse:
        covered = person.covered_by_workplace_plan or spouse_covered(case, person)
        return (0, 10000) if roth or covered else None
    if roth:
        return roth_range(case)
    return deduction_range(case, person)


def roth_range(case):
    if case.filing in {"joint", "surviving"}:
        return (236000, 246000) if rule_year(case) == 2025 else (242000, 252000)
    return (150000, 165000) if rule_year(case) == 2025 else (153000, 168000)


def deduction_range(case, person):
    if person.covered_by_workplace_plan:
        if case.filing in {"joint", "surviving"}:
            return (126000, 146000) if rule_year(case) == 2025 else (129000, 149000)
        return (79000, 89000) if rule_year(case) == 2025 else (81000, 91000)
    if case.filing == "joint" and spouse_covered(case, person):
        return (236000, 246000) if rule_year(case) == 2025 else (242000, 252000)
    return None


def reduced(limit, magi, bounds):
    """Keep full decimal precision, then apply worksheet $10/$200 rules.

    Roth uses compensation-limited base; the traditional deduction worksheet
    phases out the age-based dollar limit and applies compensation afterwards.
    Outside the phaseout, a small compensation budget is never raised to $200.
    """
    if bounds is None or magi <= bounds[0]:
        return limit
    low, high = map(Decimal, bounds)
    if magi >= high:
        return Decimal(0)
    remaining = limit * (high - magi) / (high - low)
    rounded = (remaining / 10).to_integral_value(rounding=ROUND_CEILING) * 10
    return min(limit, max(Decimal(200), rounded))


def deductible(case, person, paid):
    limit = LIMITS[rule_year(case)]["ira"]
    if age(person, case.year) >= 50:
        limit += LIMITS[rule_year(case)]["ira_catchup"]
    cap = reduced(Decimal(limit), person.traditional_ira_magi, phaseout(case, person, False))
    return min(paid, person.ira_compensation_budget, cap)
