"""Reject dates and basis histories that would make a reference appear matched."""

from datetime import date

import pytest

from wealthlab.retirement.owl_household_inputs import OwlHouseholdCase, synthetic


@pytest.mark.parametrize(
    "changes, message",
    [
        ({"start_year": 2025}, "actual current year"),
        ({"years": 11, "start_year": 2027}, "actual current year"),
        ({"federal_ira_basis": 1}, "nondeductible federal"),
        ({"nj_ira_basis": 0}, "previously-taxed NJ"),
        ({"roth_ira": 10000}, "five-year history"),
        ({"roth_ira": 10000, "roth_first_year": 2025}, "five-year history"),
        ({"age": date.today().year - 1959}, "explicit conditional"),
    ],
)
def test_unsupported_scope_is_not_silently_normalized(changes, message):
    data = synthetic().model_dump()
    with pytest.raises(ValueError, match=message):
        OwlHouseholdCase.model_validate(dict(data, **changes))
