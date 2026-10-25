"""Partial debt cures and uncertain tax elections cannot manufacture shareholder wealth."""

from decimal import Decimal

import pytest
from qoz_pooled_cases import distressed

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario


def test_a_partial_recapitalization_reduces_only_the_actual_company_creditor_balance():
    data = distressed().model_dump(mode="json")
    data["qoz_plan"]["calls"][1].update(amount="20000", recapitalization_units="20000")
    february = project(Scenario.model_validate(data))[1]
    assert february["qoz_internal_debt"] == Decimal(30000)
    assert february["qoz_nav"] == 0
    assert february["closing_cash"] == february["net_wealth"] == Decimal(35000)
    assert february["debt_balances"] == {}


def test_a_qualified_recapitalization_needs_a_supported_tax_profile_not_a_guessed_clock():
    data = distressed().model_dump(mode="json")
    data["qoz_plan"].update(federal="allowed", new_jersey="allowed")
    data["lot_plan"]["case"]["lots"][0].update(federal_basis="20000", nj_basis="30000")
    with pytest.raises(ValueError, match="separately supported tax profile"):
        project(Scenario.model_validate(data))
