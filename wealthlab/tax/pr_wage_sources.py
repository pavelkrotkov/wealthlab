"""Prepared PR wage profiles retain independent source claims and equal wage bases."""

from decimal import Decimal


def update_pr(data, binding, owner, value):
    cases = [
        *data["tax_plan"]["cases"],
        *(p["annual"] for p in data["foreign_tax_plan"]["credit_profiles"]),
    ]
    for annual in cases:
        if annual["policy"]["year"] == binding.date.year and annual["pr_federal"] is not None:
            update_source(annual["pr_federal"], binding, owner, value)


def update_source(profile, binding, owner, value):
    rows = [r for r in profile["sources"] if r["id"] == binding.source_id]
    if len(rows) != 1 or rows[0]["owner_id"] != owner:
        raise ValueError("A PR wage needs its original person/source identity.")
    row = rows[0]["income"]
    if (row["kind"], row["received"]) != ("wages", str(binding.date)):
        raise ValueError("Keep the original PR wage classification and recognition date.")
    if Decimal(row["pr_amount"]) != Decimal(row["federal_amount"]):
        raise ValueError("Different US/PR wage bases need an independently supported mapping.")
    row.update(federal_amount=str(value), pr_amount=str(value))
