"""Ordinary cash transfers cannot bypass the tranche ledger's vested-value reconciliation."""

import pytest

from wealthlab.employment.compensation_example import synthetic
from wealthlab.employment.compensation_projection import prepare
from wealthlab.household.schedules import Contribution


def test_ordinary_household_contribution_cannot_create_untracked_employer_value():
    case = synthetic()
    transfer = Contribution(
        id="bypass",
        provenance="illustration",
        start=case.start,
        end=case.end,
        monthly_amount=10,
        currency="USD",
        annual_growth=0,
        destination="employer_fund",
    )
    with pytest.raises(ValueError, match="not household cash contributions"):
        prepare(case.model_copy(update=dict(contributions=[transfer])))


def test_employer_accounts_need_tranches_and_tax_context():
    case = synthetic()
    with pytest.raises(ValueError, match="explicit household tax plan"):
        prepare(case.model_copy(update=dict(tax_plan=None)))
    extra = case.accounts[-1].model_copy(update=dict(id="untracked_employer"))
    with pytest.raises(ValueError, match="every employer account"):
        prepare(case.model_copy(update=dict(accounts=[*case.accounts, extra])))
