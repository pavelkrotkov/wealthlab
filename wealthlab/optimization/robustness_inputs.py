"""Named checks validate the frozen policy; they never select a replacement winner."""

from wealthlab.markets.inputs import MarketCase
from wealthlab.tax.facts import TaxModel


class RobustnessCheck(TaxModel):
    market: MarketCase
    required: bool = True


def validate(case):
    expected = {a.id for a in case.training.assets}
    for item in case.robustness.values():
        market = item.market
        if market.mode not in {"deterministic", "historical", "stress"}:
            raise ValueError(
                "Named robustness checks use deterministic, historical or stress mode."
            )
        if (market.start, market.end) != (case.household.start, case.household.end):
            raise ValueError("Every robustness check must cover the full household horizon.")
        if {a.id for a in market.assets} != expected:
            raise ValueError("Robustness checks must use the same named market factors.")
        if market.return_convention != case.training.return_convention:
            raise ValueError(
                "Robustness checks must preserve the return and cash-yield convention."
            )


def projection_paths(case):
    # Both the frozen selected policy and the unchanged baseline run each path.
    return 2 * sum(item.market.paths for item in case.robustness.values())
