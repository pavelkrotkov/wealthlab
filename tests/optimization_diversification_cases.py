"""Flat prices and full opening basis isolate real trading costs from assumed returns."""

from optimization_cases import flat

from wealthlab.optimization.diversification_example import extend
from wealthlab.optimization.inputs import PolicySearch


def case():
    data = extend(flat()).model_dump(mode="json")
    data["dimensions"][0]["locked_choice"] = "early"
    for market in (data["training"], data["validation"]):
        for asset in market["assets"]:
            asset.update(expected_annual_mark_return=0, annual_volatility=0, annual_cash_yield=0)
    return PolicySearch.model_validate(data)
