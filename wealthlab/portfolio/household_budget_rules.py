"""Forecast tax law and source-year carry facts match the actual household context."""

from wealthlab.tax.annual import Payments


def validate(cases, actual):
    for annual in cases:
        context = actual.get(annual.policy.year)
        if context is None:
            raise ValueError("Each budget forecast year needs the actual household tax context.")
        validate_rules(annual, context)
        if annual.payments != Payments():
            raise ValueError(
                "Budget forecasts contain liability inputs only; payments must be zero."
            )
    # Opening carry is an observed fact, not another tunable forecast. Later
    # paired carries are computed by the native report rather than entered again.
    validate_opening_carry(cases[0], actual[cases[0].policy.year])


def validate_rules(forecast, actual):
    expected = (actual.policy, actual.filing, actual.nj_filing or actual.filing, actual.nj_regime)
    supplied = (
        forecast.policy,
        forecast.filing,
        forecast.nj_filing or forecast.filing,
        forecast.nj_regime,
    )
    if supplied != expected or forecast.nj_income.retirement != actual.nj_income.retirement:
        raise ValueError(
            "Forecast filing units, tax rules and NJ retirement facts must match the household."
        )


def validate_opening_carry(forecast, actual):
    fed = (forecast.federal_income.short_carry, forecast.federal_income.long_carry)
    expected = (actual.federal_income.short_carry, actual.federal_income.long_carry)
    if fed != expected or forecast.nj_income.business.carry != actual.nj_income.business.carry:
        raise ValueError(
            "The first forecast year must preserve actual opening federal/NJ carry facts."
        )
