"""All choices retain310000original capital and261999flat closing cash after spending.

The original300000 cash/stock example is extended by exactly10000source stock.
A contribution splits that actual lot; none of the three profiles adds capital.
"""

from optimization_cases import flat

from wealthlab.optimization.exchange_example import extend
from wealthlab.optimization.inputs import PolicySearch


def case():
    data = extend(flat()).model_dump(mode="json")
    data["targets"]["maximum_issuer_weight"] = None
    data["dimensions"][0]["locked_choice"] = "early"
    data["household"]["exchange_fund_plan"]["annual_fee"] = "0"
    for path in data["exchange_opportunities"]:
        path["plan"]["annual_fee"] = "0"
    for market in (data["training"], data["validation"]):
        for asset in market["assets"]:
            asset.update(expected_annual_mark_return=0, annual_volatility=0, annual_cash_yield=0)
    return PolicySearch.model_validate(data)
