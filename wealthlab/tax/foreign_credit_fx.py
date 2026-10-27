"""A different cash refund quote does not silently make currency income tax-free.

Positive refund FX differences need a separate provided ordinary source row.
The annual bridge checks its owner, date and USD amount without choosing its
country classification. Negative currency income needs a loss profile.
"""

from decimal import Decimal


def reasons(case, cash_rows):
    income = {row.id: row for row in case.income}
    records = {row.id: row for row in case.tax_cash}
    result = []
    for row in cash_rows:
        if row["refund_fx_difference_usd"] and row["date"][:4] == str(case.annual.policy.year):
            result.extend(check(case, row, records[row["id"]], income))
    return result


def check(case, row, record, income):
    if case.fx_income_treatment == "unresolved":
        return ["Refund cash/credit FX differs; currency-income treatment is unresolved."]
    if row["refund_fx_difference_usd"] < Decimal(0):
        return ["Negative currency income requires a supported loss allocation profile."]
    fact = income.get(record.fx_income_id)
    if fact is None or fact.owner_id != record.owner_id or fact.kind != "ordinary":
        return ["Link a separate currency-income source row for the original taxpayer."]
    if (
        fact.value.date != record.value.date
        or fact.value.dollars() != row["refund_fx_difference_usd"]
    ):
        return ["Currency-income date/amount must reconcile to actual refund FX difference."]
    return []
