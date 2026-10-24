"""Actual bills need explicit net amounts, known sources and no duplicated budgets."""

import pytest
from medical_bill_cases import data

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario


@pytest.mark.parametrize(
    "change,message",
    [
        ({"date": "2025-01-01"}, "due before"),
        ({"hsa_amount": 7000}, "exceed the net"),
        ({"hsa_source": None}, "needs a source"),
        ({"hsa_source": "unknown"}, "known household HSA"),
        ({"eligibility": "unresolved"}, "medical eligibility"),
        ({"eligible_owners": ["outside"]}, "eligible HSA receipt owners"),
        ({"id": "cash_hsa"}, "IDs must be unique"),
        ({"hsa_mode": "allow_nonqualified"}, "explicit tax assumption"),
    ],
)
def test_reject_ambiguous_bill_or_distribution_scope(change, message):
    with pytest.raises(ValueError, match=message):
        project(Scenario.model_validate(data(**change)))


def test_duplicate_expenses_require_explicit_exclusion():
    value = data()
    value["hsa_plan"]["bill_expenses_excluded_from_other_inputs_confirmed"] = False
    with pytest.raises(ValueError, match="other budgets"):
        project(Scenario.model_validate(value))
