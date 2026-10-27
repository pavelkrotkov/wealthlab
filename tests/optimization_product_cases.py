"""Flat products contribute40000 capital and return it once through native exits.

There are no returns, distributions, tax gains, leverage costs or insurance
premiums in the cash identity. The only cost is the pre-existing one-dollar
brokerage exit commission; twenty-four months of living cost48000.
"""

from optimization_cases import flat

from wealthlab.optimization.inputs import PolicySearch
from wealthlab.optimization.product_example import extend


def case():
    data = extend(flat()).model_dump(mode="json")
    data["targets"]["maximum_issuer_weight"] = None
    data["dimensions"][0]["locked_choice"] = "early"
    for market in (data["training"], data["validation"]):
        for asset in market["assets"]:
            asset.update(expected_annual_mark_return=0, annual_volatility=0, annual_cash_yield=0)
    household = data["household"]
    household["exchange_fund_plan"]["annual_fee"] = "0"
    for sleeve in household["sleeve_plan"]["sleeves"]:
        for field in (
            "annual_borrow_rate",
            "annual_financing_rate",
            "annual_manager_fee",
            "turnover_cost",
            "exit_cost",
        ):
            sleeve["case"][field] = "0"
    return PolicySearch.model_validate(data)
