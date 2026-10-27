"""Separate owned books and complete reference wash context precede shared-wallet funding."""

from wealthlab.products.drilling_reference_book import SECURITY


def validate(scenario):
    drilling, option = scenario.drilling_plan, scenario.option_plan
    if drilling is None or option is None:
        return
    if drilling.account_id == option.account_id:
        raise ValueError("Drilling/options cannot share an owned household account.")
    if SECURITY in {s.wash_group for s in option.case.holdings.securities}:
        raise ValueError(
            "Drilling/options known reference wash group needs one coordinated lot-book adapter."
        )
