"""Original capital plus the supplied $600 call premium pays spending and actual taxes.

Opening wealth is $330,000: $300,000 baseline, $10,000 stock and $20,000 vested
employer value. The $80,000 contingent award is forfeited without cash. Flat
prices leave the $110 call unexercised; supplied $6/share premium stays cash.
"""

from optimization_cases import flat

from wealthlab.optimization.contract_example import extend
from wealthlab.optimization.inputs import PolicySearch


def case():
    data = extend(flat()).model_dump(mode="json")
    data["targets"]["maximum_issuer_weight"] = None
    data["dimensions"][0]["locked_choice"] = "early"
    for market in (data["training"], data["validation"]):
        for asset in market["assets"]:
            asset.update(expected_annual_mark_return=0, annual_volatility=0, annual_cash_yield=0)
    return PolicySearch.model_validate(data)
