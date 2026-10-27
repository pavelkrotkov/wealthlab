"""Wrapper examples keep independently measurable capital and actual spending identical."""

from optimization_cases import flat

from wealthlab.optimization.account_example import extend
from wealthlab.optimization.inputs import PolicySearch


def case():
    data = extend(flat()).model_dump(mode="json")
    data["targets"]["maximum_issuer_weight"] = None
    data["dimensions"][0]["locked_choice"] = "early"
    return PolicySearch.model_validate(data)
