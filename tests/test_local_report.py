"""Full audits survive export/re-import while unsupported comparisons fail before projection."""

import json
from unittest.mock import patch

import pytest

from wealthlab.household import report
from wealthlab.household.example import synthetic
from wealthlab.household.projection import project
from wealthlab.household.storage import loads
from wealthlab.tax.projection_example import template


def test_taxed_ledger_and_typed_inputs_reproduce_from_the_shared_export():
    scenario = synthetic()
    scenario = scenario.model_copy(update={"tax_plan": template(scenario)})
    rows = project(scenario)
    exported = json.loads(report.encode(report.payload(scenario, rows)))
    restored = loads(report.encode(exported))
    assert project(restored) == rows
    assert exported["taxes_modeled"] is True
    assert isinstance(exported["months"][-1]["annual_tax"], dict)
    assert exported["input_sha256"] == report.fingerprint(restored)


def test_missing_git_never_fabricates_a_reproducible_revision():
    with patch("wealthlab.household.report.subprocess.run", side_effect=FileNotFoundError):
        assert report.revision() == dict(head=None, dirty=None)


def test_unaligned_cli_comparison_is_rejected_before_running_any_projection(tmp_path):
    before, after = (
        synthetic(),
        synthetic().model_copy(update={"end": synthetic().end.replace(year=2029)}),
    )
    first, second = tmp_path / "before.json", tmp_path / "after.json"
    first.write_text(before.model_dump_json(), encoding="utf-8")
    second.write_text(after.model_dump_json(), encoding="utf-8")
    with (
        patch("wealthlab.household.report.project") as project,
        pytest.raises(ValueError, match="dates must agree"),
    ):
        report.compare(first, second)
    project.assert_not_called()
