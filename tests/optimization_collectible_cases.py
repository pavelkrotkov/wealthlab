"""Flat gold prices isolate actual sale cost and tax character from speculative returns."""

from decimal import Decimal as D

from wealthlab.optimization.collectible_example import synthetic
from wealthlab.optimization.inputs import PolicySearch


def flat():
    data = synthetic().model_dump(mode="json")
    data["targets"].update(target_age=50, reserve_years=0)
    for market in (data["training"], data["validation"]):
        market.update(paths=1, expected_annual_inflation=0, annual_inflation_volatility=0)
        market["assets"][0].update(expected_annual_mark_return=0, annual_volatility=0)
    return PolicySearch.model_validate(data)


def expected_cash():
    # 2025 Form1040 worksheet B:568500*.35-60905.50; freeze both future years.
    income_tax = D(568500) * D(".35") - D("60905.50")
    payroll = D(176100) * D(".062") + D(600000) * D(".0145") + D(350000) * D(".009")
    state = D(598000) * D(".0897") - D("17042.50")
    # One dollar commission:41999 federal collectibles gain,45999 NJ disposition.
    extra_federal = (D(41999) * D(".318")).quantize(D(".01"))
    extra_state = (D(45999) * D(".0897")).quantize(D(".01"))
    return (
        D(300000 + 1200000 - 48000 - 1)
        - 2 * (income_tax + payroll + state)
        - (extra_federal + extra_state)
    )
