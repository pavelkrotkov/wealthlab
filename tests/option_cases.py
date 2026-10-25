"""Independent small option fixtures use explicit invented contracts and tax assumptions."""

from wealthlab.products.option_example import synthetic
from wealthlab.products.option_inputs import OptionCase


def one_leg(kind="call", side="long", *, physical=False, unwind=False):
    data = synthetic("Covered call").model_dump(mode="json")
    data["legs"][0].update(
        id="contract",
        kind=kind,
        side=side,
        premium="5",
        strike="100",
        settlement="physical" if physical else "cash",
        opening_fee="0",
        closing_fee="0",
        underlying="STOCK",
        expiry="2026-01-01",
    )
    data.update(dividends=[], events=[], unwind=unwind, stock_sale_fee="0")
    data["marks"][-1].update(stock="120")
    data["tax"] = dict(
        federal_rules="conditional_capital",
        nj_rules="conditional_realized_capital",
        straddle="assume_not_applicable",
        covered_call="assume_not_applicable",
        constructive_sale="assume_not_applicable",
        holding_period="supplied_unaffected",
        nj_premium_basis="assume_same_mechanics",
    )
    return data


def parse(data):
    return OptionCase.model_validate(data)
