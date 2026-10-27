"""A whole source quote pays1000+1000premiums and2100actual surrender cash.

The supplied non-MEC ordinary100gain is below the joint deductions and NJ filing
threshold; no initial cash, basis or insurance value is added to the household.
"""

from optimization_cases import flat

from wealthlab.optimization.inputs import PolicySearch
from wealthlab.optimization.new_life_example import extend


def case():
    data = extend(flat()).model_dump(mode="json")
    data["dimensions"][0]["locked_choice"] = "early"
    data["targets"]["maximum_issuer_weight"] = None
    return PolicySearch.model_validate(data)
