"""Keep supplied partnership earnings inside the explicit SSA adapter scope.

The no-work bridge conservatively includes positive SE alongside annual wages.
The earned-W2-only work bridge rejects SE until it can classify earned months;
nonpassive income and an entered retirement date do not establish that timing.
"""

from decimal import Decimal


def add_wages(totals, year, income, fields):
    for field, owner in fields.items():
        key = year, owner
        suffix = "primary" if field == "wages_primary" else "spouse"
        se = max(Decimal(0), getattr(income, "partnership_se_earnings_" + suffix))
        totals[key] = totals.get(key, Decimal(0)) + getattr(income, field) + se


def validate_work_earnings(incomes):
    if any(i.partnership_se_earnings_primary or i.partnership_se_earnings_spouse for i in incomes):
        raise ValueError("Partnership SE needs earned-month classification for work tests.")
