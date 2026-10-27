"""Independent two-month observed price changes isolate cash and price/lock binding."""

from drilling_cases import short

from wealthlab.products.drilling_market import DrillingMarketCase
from wealthlab.products.drilling_market_example import synthetic


def price_case():
    data = synthetic().model_dump(mode="json")
    data["household"] = short(2).model_dump(mode="json")
    data["market"].update(
        end="2026-03-01",
        mode="stress",
        shocks=[
            dict(name="Commodity up ten percent", month=0, mark_shocks={"commodity": 0.1}),
            dict(
                name="Independent second month",
                month=1,
                mark_shocks={"commodity": -0.1, "reference": 0.2},
            ),
        ],
    )
    for asset in data["market"]["assets"]:
        asset.update(expected_annual_mark_return=0, annual_volatility=0)
    return DrillingMarketCase.model_validate(data)


def edited(configure):
    data = price_case().model_dump(mode="json")
    configure(data)
    return DrillingMarketCase.model_validate(data)
