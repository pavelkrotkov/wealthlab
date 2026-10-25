"""A confirmed actual qualified-plan receipt cannot silently become another transfer type."""

import pytest
from pydantic import ValidationError

from wealthlab.retirement.distribution_inputs import DistributionCase
from wealthlab.retirement.ira_rollover_example import synthetic


@pytest.mark.parametrize(
    "change,message",
    [
        (dict(destination="roth"), "traditional IRA destination"),
        (dict(owner="other"), "keeps its owner"),
        (dict(source="ira"), "outside the IRA book"),
        (dict(date="2027-01-01"), "selected year"),
        (dict(provenance="unresolved"), "Resolve"),
        (dict(id="draw_0"), "unique"),
    ],
)
def test_dates_owner_identity_and_account_scope_are_validated(change, message):
    data = synthetic().model_dump(mode="json")
    data["incoming_rollovers"][0].update(change)
    with pytest.raises(ValidationError, match=message):
        DistributionCase.model_validate(data)


@pytest.mark.parametrize(
    "field",
    [
        "eligible_direct_rollover_and_rmd_excluded_confirmed",
        "independent_basis_and_no_special_features_confirmed",
        "excluded_from_opening_balances_and_cash_receipts_confirmed",
    ],
)
def test_unknown_eligibility_basis_or_duplicate_cash_is_blocked(field):
    data = synthetic().model_dump(mode="json")
    data["incoming_rollovers"][0][field] = False
    with pytest.raises(ValidationError, match="Confirm"):
        DistributionCase.model_validate(data)


@pytest.mark.parametrize("field", ["federal_basis_transferred", "nj_basis_transferred"])
def test_transferred_aftertax_component_cannot_exceed_the_supported_cash_receipt(field):
    data = synthetic().model_dump(mode="json")
    data["incoming_rollovers"][0][field] = 20001
    with pytest.raises(ValidationError, match="basis no greater"):
        DistributionCase.model_validate(data)
