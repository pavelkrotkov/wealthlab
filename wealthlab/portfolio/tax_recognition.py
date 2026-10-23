"""Aggregate dated recognized lot gains without treating pending losses as deductions."""

from datetime import date
from decimal import Decimal

from wealthlab.tax.annual import AnnualCase


def gains(book, year):
    totals = dict(short_term=Decimal(0), long_term=Decimal(0), collectibles_component=Decimal(0))
    nj = Decimal(0)
    pending = {jurisdiction: Decimal(0) for jurisdiction in ("federal", "nj")}
    for row in book.disposals:
        if date.fromisoformat(row["date"]).year != year:
            continue
        value = row["federal_recognized_gain"]
        totals[row["federal_character"]] += value
        if (
            book.securities[row["security_id"]].kind == "collectible"
            and row["federal_character"] == "long_term"
        ):
            totals["collectibles_component"] += value
        nj += row["nj_recognized_gain"]
        for jurisdiction in pending:
            pending[jurisdiction] += row[jurisdiction + "_pending_loss"]
    return totals, nj, pending


def with_gains(case, federal, nj):
    """Baseline income excludes these modeled disposals; deductions remain as supplied."""
    payload = case.model_dump()
    for field, value in federal.items():
        payload["federal_income"][field] += value
    payload["nj_income"]["dispositions"] += nj
    return AnnualCase.model_validate(payload)


def with_carry(case, result):
    if result is None:
        return case
    payload = case.model_dump()
    # Each compared scenario supplies its own prior result; a harvested loss
    # must never reduce the counterfactual baseline's later capital gains.
    payload["federal_income"]["short_carry"] = result["federal"]["short_carry"]
    payload["federal_income"]["long_carry"] = result["federal"]["long_carry"]
    return AnnualCase.model_validate(payload)
