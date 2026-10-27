"""Report executed fee bills, actual paid cash and remaining modeled liabilities separately."""

from statistics import median


def actual(result):
    paths = [item["rows"] for item in result["details"]]
    validate_observed(result, paths)
    return dict(
        median_advisory_fees_assessed=median(
            sum(row.get("advisory_fees_assessed", 0) for row in rows) for rows in paths
        ),
        median_advisory_fees_paid=median(
            sum(row.get("advisory_fees_paid", 0) for row in rows) for rows in paths
        ),
        maximum_ending_advisory_fees_owed=max(
            rows[-1].get("advisory_fees_owed", 0) for rows in paths
        ),
    )


def validate_observed(result, paths):
    if result.get("household", {}).get("advisory_fee_plan") is None:
        return
    fields = ("advisory_fees_assessed", "advisory_fees_paid", "advisory_fees_owed")
    if not all(all(key in row for key in fields) for rows in paths for row in rows):
        raise ValueError(
            "Actual advisory fee observations are required; unknown costs are not zero."
        )
