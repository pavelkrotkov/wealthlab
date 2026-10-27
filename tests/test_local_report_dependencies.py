"""Production retirement tables must be identifiable even in a mismatched environment."""

import json
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

import pytest

from wealthlab import cli
from wealthlab.household import report
from wealthlab.household.example import synthetic


@pytest.mark.parametrize("installed", ["2026.10.10", "2099.1.0", None])
def test_report_records_actual_owl_metadata_or_explicit_absence(monkeypatch, installed):
    def metadata(name):
        if name != "owlplanner":
            return version(name)
        if installed is None:
            raise PackageNotFoundError(name)
        return installed

    monkeypatch.setattr(report, "version", metadata)
    payload = json.loads(report.encode(report.payload(synthetic(), [])))
    assert "owlplanner" in payload["dependencies"]
    assert payload["dependencies"]["owlplanner"] == installed
    assert payload["dependencies"]["taxcalc"] == version("taxcalc")


def test_native_cli_reports_the_actual_installed_owl_table_version(capsys):
    source = Path(__file__).resolve().parents[1] / "examples/synthetic.json"
    assert cli.main(["project", str(source)]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["dependencies"]["owlplanner"] == version("owlplanner")
    assert payload["months"][-1]["net_wealth"] == "224000.00"
