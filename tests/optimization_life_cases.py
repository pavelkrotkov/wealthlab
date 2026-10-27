"""Same opening policy, supplied complete paths and flat independent cash expectations."""

from optimization_cases import flat

from wealthlab.optimization.inputs import PolicySearch
from wealthlab.optimization.life_example import extend


def case():
    data = extend(flat()).model_dump(mode="json")
    data["dimensions"][0]["locked_choice"] = "early"
    data["targets"]["maximum_issuer_weight"] = None
    return PolicySearch.model_validate(data)
