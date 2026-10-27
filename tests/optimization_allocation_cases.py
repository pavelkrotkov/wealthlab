"""Flat markets leave only original spending/commission and independently enabled product costs."""

from optimization_cases import flat

from wealthlab.optimization.allocation_example import extend
from wealthlab.optimization.inputs import PolicySearch


def case():
    data = extend(flat()).model_dump(mode="json")
    data["targets"]["maximum_issuer_weight"] = None
    data["dimensions"][0]["locked_choice"] = "early"
    for opportunity in data["sleeve_opportunities"]:
        product = opportunity["unit"]["case"]
        product["rebalance"] = "none"
        for field in (
            "annual_borrow_rate",
            "annual_financing_rate",
            "annual_manager_fee",
            "turnover_cost",
            "exit_cost",
        ):
            product[field] = "0"
    return PolicySearch.model_validate(data)
