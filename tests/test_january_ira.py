"""Pending eligibility must be decided after observations, even with zero tax delta."""

import pytest

from tests.january_ira_cases import case
from wealthlab.household.projection import project


def test_funded_roth_is_finally_eligible_after_the_original_year_loss_is_allowed():
    rows = project(case())
    assert (
        rows[11]["ira_contribution_eligibility"]["status"] == "pending_january_wash_reconciliation"
    )
    audit = rows[-1]["lot_audit"]["return_reconciliations"][0]
    assert audit["ira_eligibility"]["roth_ira_magi"] == 236000
    assert audit["ira_eligibility"]["status"] == "checked_supported_annual_w2_case"


def test_january_replacement_cannot_preserve_an_ineligible_funded_roth():
    with pytest.raises(ValueError, match="Funded Roth IRA contributions exceed"):
        project(case(repurchase=True))
