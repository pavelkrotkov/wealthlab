"""Native CLI replay retains Spain facts and discards invented archived outcomes.

A mixed comparison executes the ordinary baseline and native country candidate
on the same dates. The existing Spain cash fixture supplies all financial rules;
this check verifies the previously missing report/command workflow only.
"""

import json
from decimal import Decimal

from test_local_cli import invoke

from wealthlab import country_report
from wealthlab.household.report import encode
from wealthlab.tax.jurisdiction_execution_example import synthetic


def command(args, directory):
    result = invoke(args, directory)
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def test_spain_cli_replay_and_ordinary_country_comparison_preserve_complete_context(tmp_path):
    case = synthetic("Spain")
    source = tmp_path / "country.json"
    source.write_text(case.model_dump_json())
    original = command(["project", str(source)], tmp_path)
    assert (
        original["format"],
        original["inputs"]["spain"],
        bool(original["source_revision"]["head"]),
        bool(original["dependencies"]["taxcalc"]),
    ) == (country_report.FORMAT, case.spain.model_dump(mode="json"), True, True)
    original["months"][-1]["net_wealth"] = "999999999999"
    archive = tmp_path / "country-audit.json"
    archive.write_text(encode(original))
    fresh = command(["project", str(archive)], tmp_path)
    assert fresh["months"][-1]["net_wealth"] != "999999999999"
    assert (fresh["input_sha256"], fresh["country_assessments"]) == (
        original["input_sha256"],
        original["country_assessments"],
    )
    ordinary = tmp_path / "ordinary.json"
    ordinary.write_text(
        case.scenario.model_copy(update=dict(foreign_tax_plan=None)).model_dump_json()
    )
    result = command(["compare", str(ordinary), str(archive)], tmp_path)
    assert result["candidate"]["months"] == fresh["months"]
    before = Decimal(result["baseline"]["months"][-1]["net_wealth"])
    after = Decimal(fresh["months"][-1]["net_wealth"])
    assert Decimal(result["ending_wealth_change_usd"]) == after - before != 0
