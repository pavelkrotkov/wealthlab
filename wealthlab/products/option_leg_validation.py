"""Contract-style and explicit year-end recognition coverage checks."""

from datetime import date


def validate_leg(case, leg, dates):
    """Cash index delivery and physical stock delivery are separate contracts.

    A pricing engine never supplies legal section1256 status or an actual roll.
    """
    if leg.provenance == "unresolved" or not dates[0] <= leg.opened < leg.expiry:
        raise ValueError("Resolve option terms and supply a valid open/expiry date.")
    validate_dates(leg, dates)
    if leg.underlying == "INDEX" and leg.settlement == "physical":
        raise ValueError("Physical index delivery is unsupported; enter actual cash settlement.")
    validate_classification(leg, dates)
    if leg.rolls_to and leg.rolls_to not in {item.id for item in case.legs}:
        raise ValueError("Roll target must be a separately priced, dated option leg.")


def validate_classification(leg, dates):
    if leg.federal_class == "section1256" and leg.settlement != "cash":
        raise ValueError("The conditional section1256 path supports cash settlement only.")
    if leg.side == "short" and leg.federal_character != "short_term":
        raise ValueError(
            "Written capital options use short-term character; special cases are unresolved."
        )
    if leg.federal_class == "section1256":
        for year in range(leg.opened.year, min(leg.expiry.year, dates[-1].year)):
            if date(year, 12, 31) not in dates:
                raise ValueError("Conditional 1256 year-end recognition needs a December 31 mark.")


def validate_dates(leg, dates):
    if leg.opened not in dates or (leg.expiry <= dates[-1] and leg.expiry not in dates):
        raise ValueError("Every opening and in-period expiry requires a dated mark.")
