"""Actual realization dates determine character for a confirmed ordinary holding period.

New cash-only subscriptions cannot inherit an older interest's conditional
long-term label. Deferred loss recognition retains the character established
on the actual cash realization date, not the later assumed release date.
"""

from wealthlab.portfolio.disposal import is_long


def character(contract, realized):
    start = contract.federal_holding_start
    if start is None:
        return contract.federal_capital_character
    if realized < start:
        raise ValueError("Fund realization cannot precede the supplied holding start.")
    return "long_term" if is_long(start, realized) else "short_term"


def validate_profile(contract):
    dated = contract.federal_holding_start is not None
    if dated == (contract.federal_capital_character is not None):
        raise ValueError(
            "Supply either a holding start or conditional capital character, not both."
        )
    if dated and not contract.ordinary_holding_period_assumed_confirmed:
        raise ValueError(
            "Confirm ordinary holding-period rules, excluding section1061 and tacking."
        )
