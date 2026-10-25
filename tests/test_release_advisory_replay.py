"""Imported fee inputs cannot create wealth, erase debt or write to code checkouts."""

import json
from decimal import Decimal

import pytest
from test_local_cli import invoke

from tests.optimizer_advisory_cases import case
from wealthlab.household.report import encode
from wealthlab.optimization import report
from wealthlab.optimization.inputs import PolicySearch


def test_fee_contract_edit_cannot_keep_an_old_policy_search_fingerprint():
    archive = report.payload(dict(inputs=case().model_dump(mode="json")))
    archive["inputs"]["household"]["advisory_fee_plan"]["schedules"][0]["tiers"][0][
        "annual_rate"
    ] = "0"
    with pytest.raises(ValueError, match="fingerprint"):
        report.loads(encode(archive))


def test_actual_cli_fee_debt_cannot_become_a_completed_after_tax_exit(tmp_path):
    data = case().model_dump(mode="json")
    schedule = data["household"]["advisory_fee_plan"]["schedules"][0]
    schedule.update(tiers=[dict(upper_limit=None, annual_rate="0")], fixed_per_period="350000")
    profile = PolicySearch.model_validate(data)
    source = tmp_path / "synthetic-unfunded-fee.json"
    source.write_text(profile.model_dump_json(), encoding="utf-8")
    process = invoke(["optimize", str(source)], tmp_path)
    assert process.returncode == 0, process.stderr
    result = json.loads(process.stdout)
    first = result["candidates"][0]
    assert sum(a.balance for a in profile.household.accounts) == 300000
    assert Decimal(first["median_advisory_fees_paid"]) == 253999
    assert Decimal(first["maximum_ending_advisory_fees_owed"]) == 96001
    assert first["median_real_after_tax_exit_wealth"] is None
    assert result["selection"] is None and result["held_out"] is None
    assert sorted(p.name for p in tmp_path.iterdir()) == [source.name]
