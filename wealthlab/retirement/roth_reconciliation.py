"""Owner-wide regular contributions, annual conversion buckets, then earnings."""

from calendar import monthrange
from datetime import date
from decimal import Decimal

from wealthlab.retirement.roth_nj import reconcile as nj_reconcile


def half_birthday(birth):
    months = birth.year * 12 + birth.month - 1 + 59 * 12 + 6
    year, month = divmod(months, 12)
    month += 1
    return date(year, month, min(birth.day, monthrange(year, month)[1]))


def conversion_buckets(case, book, person):
    buckets = [entry.model_dump() for entry in sorted(person.conversions, key=lambda e: e.year)]
    rows = [r for r in book["rows"] if r["owner"] == person.id and r["kind"] == "conversion"]
    total = sum((row["paid"] for row in rows), Decimal(0))
    if total:
        taxable = sum((row["federal_taxable"] for row in rows), Decimal(0))
        buckets.append(
            dict(year=case.year, taxable_remaining=taxable, nontaxable_remaining=total - taxable)
        )
    return buckets, total


def draw_conversions(buckets, amount, when):
    consumed, recapture = Decimal(0), Decimal(0)
    for bucket in buckets:
        for key in ("taxable_remaining", "nontaxable_remaining"):
            paid = min(amount - consumed, bucket[key])
            bucket[key] -= paid
            consumed += paid
            if key == "taxable_remaining" and when.year < bucket["year"] + 5:
                recapture += paid
    return consumed, recapture


def reconcile(case, book, person):
    rows = [r for r in book["rows"] if r["owner"] == person.id and r["wrapper"] == "roth"]
    buckets, converted = conversion_buckets(case, book, person)
    first = person.roth_first_year
    if first is None and converted:
        first = case.year
    regular = person.roth_regular_basis
    for row in rows:
        regular = federal_draw(person, row, regular, buckets, first)
    remaining = nj_reconcile(book, person, rows, converted)
    return dict(
        roth_regular_basis=regular,
        conversions=buckets,
        nj_roth_basis=remaining,
        roth_first_year=first,
    )


def federal_draw(person, row, regular, buckets, first):
    """Nonqualified federal distributions consume annual owner-wide pools.

    Tax recognition can depend on later funded conversions in the same year;
    cash chronology remains separate and never borrows those future assets.
    """
    qualified = first is not None and row["date"].year >= first + 5
    qualified = qualified and row["date"] >= half_birthday(person.birth_date)
    row["roth_qualified"] = qualified
    row["federal_taxable"], row["conversion_recapture"] = Decimal(0), Decimal(0)
    contribution = min(row["paid"], regular)
    used, recapture = draw_conversions(buckets, row["paid"] - contribution, row["date"])
    row["federal_taxable"] = 0 if qualified else row["paid"] - contribution - used
    row["conversion_recapture"] = 0 if qualified else recapture
    return regular - contribution
