"""New source election support does not broaden unrelated clocks or reset used gain."""

from datetime import date
from decimal import Decimal

import pytest
from qoz_transition_cases import transition
from return_reconciliation_cases import allowed_loss, close_december

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.tax.return_reconciliation import revise


def test_existing_wash_revision_entry_point_still_rejects_february():
    taxes, _ = close_december(100000)
    with pytest.raises(ValueError, match="observes January"):
        revise(taxes, 2026, allowed_loss(taxes), date(2027, 2, 28))


def test_mandatory_legacy_inclusion_does_not_refresh_the_original_gains_eligibility():
    data = transition().model_dump(mode="json")
    second = data["qoz_plan"]["calls"][0]
    first = dict(second, id="legacy_call", date="2026-12-31")
    second["amount"] = "1000"
    data["qoz_plan"]["calls"] = [first, second]
    rows = project(Scenario.model_validate(data))
    assert rows[11]["qoz_original_gain_included"] == Decimal(80000)
    calls = rows[-1]["qoz_audit"]["calls"]
    assert calls[1]["funded"] == Decimal(1000)
    assert calls[1]["elected"] == dict(federal=0, new_jersey=0)
    assert rows[-1]["qoz_audit"]["source_return_revisions"] == []


def test_a_deemed_inclusion_tax_event_is_not_an_actual_stock_disposal_source():
    data = transition().model_dump(mode="json")
    data["tax_plan"]["events"].append(
        dict(
            date="2026-12-31",
            description="legacy_deemed_inclusion",
            cash_received="0",
            federal=dict(long_term="80000"),
            new_jersey=dict(dispositions="80000"),
        )
    )
    data["qoz_plan"]["calls"][0]["source_trade_id"] = "legacy_deemed_inclusion"
    with pytest.raises(ValueError, match="already executed source disposal"):
        project(Scenario.model_validate(data))
