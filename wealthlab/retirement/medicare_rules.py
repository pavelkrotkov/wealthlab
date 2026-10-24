"""Published 2026 full Part B and Part D IRMAA schedules; future indexing is conditional."""

from decimal import Decimal, localcontext

from wealthlab.household.calendar import money

# CMS November 14, 2025 fact sheet. The last tier starts AT its threshold,
# whereas intermediate tiers start only ABOVE theirs. Keep that distinction.
B_PREMIUMS = ("202.90", "284.10", "405.80", "527.50", "649.20", "689.90")
D_SURCHARGES = ("0", "14.50", "37.50", "60.40", "83.30", "91.00")
LIMITS = dict(
    individual=(109000, 137000, 171000, 205000, 500000),
    joint=(218000, 274000, 342000, 410000, 750000),
)
SOURCE = "https://www.cms.gov/newsroom/fact-sheets/2026-medicare-parts-b-premiums-deductibles"


def scale(case, year, amount, kind):
    growth = Decimal(0)
    if case.future_policy == "index_2026_assumption":
        growth = case.premium_growth if kind == "premium" else case.threshold_growth
    with localcontext() as context:
        context.prec = 64
        projected = Decimal(amount) * (1 + growth) ** (year - 2026)
        if projected > Decimal("9999999999999999.99"):
            raise ValueError("Projected Medicare amounts exceed the supported monetary range.")
        return money(projected)


def tier(case, year, filing, magi):
    if filing == "separate_lived_together":
        lower = scale(case, year, 109000, "threshold")
        upper = scale(case, year, 391000, "threshold")
        if magi >= upper:
            return 5
        return 4 if magi > lower else 0
    status = "joint" if filing == "joint" else "individual"
    limits = [scale(case, year, value, "threshold") for value in LIMITS[status]]
    if magi >= limits[-1]:
        return 5
    return sum(magi > limit for limit in limits[:-1])


def premiums(case, year, income):
    magi = income.agi + income.tax_exempt_interest
    index = tier(case, year, income.filing, magi)
    standard = scale(case, year, B_PREMIUMS[0], "premium")
    total = scale(case, year, B_PREMIUMS[index], "premium")
    return dict(
        magi=magi,
        tier=index,
        b_standard=standard,
        b_irmaa=total - standard,
        b_total=total,
        d_irmaa=scale(case, year, D_SURCHARGES[index], "premium"),
    )
