"""Schedule A2 ordinary/15% comparison and separate Act60 in-lieu tax buckets."""

from decimal import Decimal

from wealthlab.household.calendar import money
from wealthlab.tax.pr_credit_allocation import allocation
from wealthlab.tax.pr_credit_limit import limited
from wealthlab.tax.pr_local_rates import abt, regular
from wealthlab.tax.pr_residence import MET

RATES = {
    "lt15": Decimal(".15"),
    "special0": Decimal(0),
    "special4": Decimal(".04"),
    "special5": Decimal(".05"),
}


def calculate(annual, slices, us_paid):
    totals = grouped(slices)
    gross = sum(totals.values(), Decimal(0))
    exemption = Decimal(7000 if annual.baseline.filing.status == "joint" else 3500)
    # Schedule A2 applies personal exemptions only to ordinary income.
    # Additional deductions need rounded percentage allocation and stay guarded.
    ordinary = max(Decimal(0), totals["ordinary"] - exemption)
    normal = regular(ordinary, exemption, gross)
    preferred = normal["tax"] + money(totals["lt15"] * RATES["lt15"])
    alternative = regular(
        max(Decimal(0), totals["ordinary"] + totals["lt15"] - exemption), exemption, gross
    )
    # A2 permits the less expensive all-ordinary alternative before credits.
    # Ordinary 15%-eligible gains remain in the general ABT base.
    regular_tax = min(preferred, alternative["tax"])
    # Act60 0/4/5 buckets replace ABT on those same amounts; add the special
    # tax once after comparing the regular and ABT tax on other income.
    special = money(sum((totals[key] * RATES[key] for key in RATES if key != "lt15"), Decimal(0)))
    base = max(Decimal(0), totals["ordinary"] + totals["lt15"] - exemption)
    tentative = abt(base, wage_only=wage_only(annual, slices))
    # A2 line11 retains the signed ordinary column before summing A-H for C.
    a2_ordinary = totals["ordinary"] - exemption
    a2_base = max(Decimal(0), a2_ordinary + totals["lt15"])
    source = source_allocation(slices, exemption)
    credit = limited(regular_tax, us_paid, source["source_net"], a2_base)
    alternate_credit = limited(tentative, us_paid, source["source_net"], base)
    regular_net = regular_tax - credit["allowed"]
    alternate_net = tentative - alternate_credit["allowed"]
    return dict(
        gross=gross,
        groups=totals,
        exemption=exemption,
        ordinary_net=ordinary,
        preferred_tax=preferred,
        all_ordinary_tax=alternative["tax"],
        regular_tax=regular_tax,
        special_in_lieu_tax=special,
        regular_credit=credit,
        a2_ordinary_net_before_tax_floor=a2_ordinary,
        regular_net_income=a2_base,
        regular_source_allocation=source,
        abt_net_income=base,
        abt=tentative,
        abt_credit=alternate_credit,
        abt_source_allocation=source,
        additional_abt=max(Decimal(0), alternate_net - regular_net),
        income_tax=max(regular_net, alternate_net) + special,
        next_abt_credit=max(Decimal(0), alternate_net - regular_net),
        allocation="No additional PR deductions; exemption reduces ordinary income only",
    )


def grouped(slices):
    totals = dict.fromkeys(["ordinary", *RATES], Decimal(0))
    for item in slices:
        totals[item.treatment] += item.row.pr_amount
    return totals


def source_allocation(slices, exemption):
    eligible = [item.row for item in slices if item.treatment in {"ordinary", "lt15"}]
    gross = sum((row.pr_amount for row in eligible), Decimal(0))
    foreign = sum((row.pr_amount for row in eligible if row.pr_source == "US"), Decimal(0))
    return allocation(gross, foreign, exemption)


def wage_only(annual, slices):
    return (
        all(item.row.kind == "wages" for item in slices)
        and annual.pr_wages_reported_on_form_499r2 in MET
    )
