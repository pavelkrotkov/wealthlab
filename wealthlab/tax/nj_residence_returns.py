"""Calculate each NJ period before applying the nonresident source percentage.

NJ-1040NR computes tax on worldwide income during nonresidence, not directly
on NJ-source taxable income. The four-decimal column B/A percentage may exceed
one when an out-of-state loss reduces column A. Resident/nonresident exemptions
use their independently counted fifteen-day months; expenses use actual periods.
"""

from decimal import ROUND_HALF_UP, Decimal

from wealthlab.household.calendar import money
from wealthlab.tax import nj_residence_deductions as expense
from wealthlab.tax.nj_rates import tax
from wealthlab.tax.nj_residence_calendar import months, year_days
from wealthlab.tax.nj_residence_income import columns, gross, totals

ZERO = Decimal(0)


def calculate_unit(profile, unit, year):
    owners, filing, resident = unit["owners"], unit["filing"], unit["days"]
    all_rows = [r for r in profile.income if r.owner_id in owners]
    observed = [r for r in all_rows if r.received <= profile.as_of]
    inside, outside, sourced = columns(observed, resident)
    full_gross = gross(totals(all_rows))
    below = full_gross <= (10000 if filing.status in {"single", "separate"} else 20000)
    result = []
    for kind, values, source_values, days in (
        ("resident", inside, inside, resident),
        ("nonresident", outside, sourced, year_days(year) - resident),
    ):
        if not days:
            continue
        count = months(days, year)
        deducted = expense.amount(
            gross(values), filing, expense.period_inputs(profile, unit, kind, days), count
        )
        item = period_return(kind, filing, values, source_values, deducted, below)
        item.update(
            id=f"nj:{year}:{'+'.join(owners)}:{kind}",
            owners=owners,
            year=year,
            period=kind,
            months=count,
            filing_status=filing.status,
            full_year_worldwide_gross=full_gross,
            prorated_exemptions=expense.prorated_exemption(filing, count),
        )
        result.append(item)
    return result


def period_return(kind, filing, values, source_values, deducted, below):
    worldwide, nj_source = gross(values), gross(source_values)
    if kind == "nonresident" and worldwide == 0 and nj_source:
        raise ValueError(
            "NJ nonresident zero worldwide denominator needs a separately supported return."
        )
    ratio = (
        Decimal(1)
        if kind == "resident"
        else (
            (nj_source / worldwide).quantize(Decimal(".0001"), rounding=ROUND_HALF_UP)
            if worldwide
            else ZERO
        )
    )
    taxable = max(ZERO, worldwide - deducted)
    before = ZERO if below or taxable == 0 else tax(taxable, filing.status)
    return dict(
        column_a=worldwide,
        column_b=nj_source,
        income_percentage=ratio,
        taxable_income=taxable,
        deductions=deducted,
        tax_before_source_percentage=before,
        income_tax=money(before * ratio),
        below_filing_threshold=below,
    )
