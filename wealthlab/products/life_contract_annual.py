"""Compare explicit annual baselines; tax changes are liabilities, never cash receipts."""

from wealthlab.tax.annual import AnnualCase, evaluate

FIELDS = ("federal_ordinary_income", "federal_additional_tax", "nj_ordinary_income")


def compare(case, rows):
    years = sorted({int(row["date"][:4]) for row in rows})
    return [annual(case, year, [r for r in rows if int(r["date"][:4]) == year]) for year in years]


def annual(case, year, rows):
    unknown, amounts = recognition(rows)
    result = dict(year=year, recognition=amounts, unknown_fields=unknown, tax_change=None)
    if unknown:
        return dict(result, status="unknown recognition: no annual tax conclusion")
    baseline = case.annual_cases.get(year)
    if baseline is None:
        return dict(result, status="missing annual baseline: recognized amounts only")
    if baseline.policy.year != year:
        raise ValueError("Policy annual baseline key must match its tax year.")
    data = baseline.model_dump()
    data["federal_income"]["insurance_ordinary_income"] += amounts["federal_ordinary_income"]
    data["federal_income"]["insurance_additional_tax"] += amounts["federal_additional_tax"]
    data["nj_income"]["other"] += amounts["nj_ordinary_income"]
    before, after = evaluate(baseline), evaluate(AnnualCase.model_validate(data))
    result.update(
        status="conditional annual liability; no payment or refund executed",
        baseline=before,
        with_policy=after,
        tax_change=after["total_liability"] - before["total_liability"],
    )
    return result


def recognition(rows):
    unknown, amounts = [], {}
    for field in FIELDS:
        values = [row[field] for row in rows]
        if None in values:
            unknown.append(field)
        else:
            amounts[field] = sum(values)
    return unknown, amounts
