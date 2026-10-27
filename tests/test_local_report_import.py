"""Projection envelopes load validated inputs only; archived outcomes are never trusted as facts."""

import json
from decimal import Decimal

import pytest

from wealthlab.household.example import synthetic
from wealthlab.household.report import encode, payload
from wealthlab.household.storage import fingerprint, loads


def test_imported_report_ignores_archived_outcomes_and_preserves_source_identity():
    scenario = synthetic()
    archive = payload(scenario, [{"net_wealth": "invented archived outcome"}])
    restored = loads(encode(archive))
    assert fingerprint(restored) == fingerprint(scenario)
    assert restored == scenario


def test_changed_report_inputs_cannot_retain_the_original_reproduction_fingerprint():
    archive = payload(synthetic(), [])
    archive["inputs"]["name"] = "Changed inputs"
    with pytest.raises(ValueError, match="fingerprint"):
        loads(encode(archive))


def test_numeric_json_money_preserves_cents_at_the_supported_precision_boundary():
    data = synthetic().model_dump(mode="json")
    raw = json.dumps(data).replace('"balance": "100000"', '"balance": 9999999999999999.99', 1)
    assert loads(raw).accounts[0].balance == Decimal("9999999999999999.99")
