"""Either product validator rejects duplicate capital and unsupported shared wash context."""

import pytest
from drilling_option_cases import conflict

from wealthlab.household.projection import project
from wealthlab.products.drilling_accounts import validate_account
from wealthlab.products.option_exchange_accounts import validate as validate_options


def validate_drilling(case):
    validate_account(case, case.drilling_plan)


@pytest.mark.parametrize("validator", [validate_drilling, validate_options, project])
@pytest.mark.parametrize("kind", ["account", "wash"])
def test_both_entry_points_reject_contradictory_owned_books(validator, kind):
    with pytest.raises(ValueError, match="Drilling/options"):
        validator(conflict(kind))
