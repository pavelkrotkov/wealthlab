"""Use the actual lookback return; retirement does not automatically erase IRMAA.

A supplied current-income determination is a conditional scenario, never an
approved SSA-44 appeal. Three-year fallback is allowed only when the normal
two-year return is absent and the user confirms the older return was selected.
"""


def income_for(case, member, year):
    adjustments = [d for d in case.determinations if d.member == member and d.premium_year == year]
    if adjustments:
        determination = adjustments[0]
        income = next(i for i in case.income_history if i.id == determination.income)
        return income, determination.method
    income = history_index(case).get((member, year - 2))
    if income is None:
        raise ValueError(f"Missing two-year Medicare income history for {member}, {year}.")
    return income, "two_year_lookback"


def validate_determination(case, item, incomes):
    income = incomes.get(item.income)
    if income is None or item.member not in income.members:
        raise ValueError("Medicare determination requires the member's known income record.")
    if not case.start_year <= item.premium_year < case.end_year:
        raise ValueError("Medicare determination year is outside the projection.")
    if item.method == "three_year_fallback_confirmed":
        validate_fallback(case, item, income)
    elif income.year not in (item.premium_year - 1, item.premium_year):
        raise ValueError("Conditional redetermination needs the prior or current year's income.")


def validate_fallback(case, item, income):
    if income.year != item.premium_year - 3:
        raise ValueError("Medicare fallback income must be three years before the premium year.")
    available = any(
        i.year == item.premium_year - 2 and item.member in i.members for i in case.income_history
    )
    if available:
        raise ValueError("Three-year fallback cannot replace available two-year income history.")


def history_index(case):
    return {
        (member, income.year): income for income in case.income_history for member in income.members
    }
