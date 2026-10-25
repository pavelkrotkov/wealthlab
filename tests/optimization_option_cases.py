"""Flat supplied quotes give a $496 net gain per actually purchased option unit.

Each unit receives500premium less1opening contract fee and pays2purchase/1sale
commissions. Original300000 capital pays48000living costs and1existing-stock
commission; the12k option allocation only transfers existing household capital.
"""

from optimization_cases import flat

from wealthlab.optimization.inputs import PolicySearch
from wealthlab.optimization.option_allocation_example import extend


def case():
    data = extend(flat()).model_dump(mode="json")
    data["targets"]["maximum_issuer_weight"] = None
    data["dimensions"][0]["locked_choice"] = "early"
    for market in (data["training"], data["validation"]):
        for asset in market["assets"]:
            asset.update(expected_annual_mark_return=0, annual_volatility=0, annual_cash_yield=0)
    return PolicySearch.model_validate(data)
