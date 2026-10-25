"""Require actual observation dates; never interpolate quotes for exercise or rolls."""

from datetime import timedelta

from wealthlab.household.calendar import months


def validate_dates(scenario):
    case = scenario.option_plan.case
    allowed = {
        scenario.start,
        *(end - timedelta(days=1) for _, end in months(scenario.start, scenario.end)),
    }
    for leg in case.legs:
        validate_leg(leg, scenario.start, case.holdings.end, allowed)
    validate_cash_dates(case, allowed)


def validate_leg(leg, start, end, allowed):
    if leg.opened != start or leg.rolls_to:
        raise ValueError(
            "Option paths support opening contracts only; roll quotes are unavailable."
        )
    if leg.expiry <= end and leg.expiry not in allowed:
        raise ValueError("Intramonth option expiry needs a dated settlement-price adapter.")


def validate_cash_dates(case, allowed):
    for event in case.events:
        if event.date not in allowed or event.action == "close":
            raise ValueError(
                "Option paths need month-end exercise/expiry; close quotes cannot be reused."
            )
    for dividend in case.dividends:
        if dividend.ex_date not in allowed or dividend.pay_date not in allowed:
            raise ValueError("Intramonth dividends need dated entitlement and price observations.")
