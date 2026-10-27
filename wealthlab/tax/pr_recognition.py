"""Local part-year worldwide income plus PR-source receipts outside residence."""

from wealthlab.tax.pr_residence import local_period


def recognized(case):
    rows = []
    for row in case.income:
        residence = getattr(case, row.owner)
        period = local_period(residence, case.baseline.policy.year)
        if period is None:
            raise ValueError("Every income owner's local residence period must be explicit.")
        if row.pr_source == "PR" or period[0] <= row.received <= period[1]:
            rows.append(row)
    return rows
