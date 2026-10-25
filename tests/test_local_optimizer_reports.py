"""Re-import recomputes a search rather than trusting archived outcomes or validation success."""

import pytest
from optimization_cases import flat

from wealthlab.household.report import encode
from wealthlab.household.storage import MAX_BYTES, fingerprint
from wealthlab.optimization import report


def test_report_reimport_discards_forged_archived_selection_and_reexecutes_actual_cash(tmp_path):
    source = tmp_path / "case.json"
    source.write_text(flat().model_dump_json())
    first = report.run(source)
    archive = dict(first, selection="invented", candidates=[], configured_validation_passed=True)
    source.write_text(encode(archive))
    second = report.run(source)
    assert second == first
    assert second["candidates"][0]["median_real_after_tax_exit_wealth"] == 251999


def test_changed_allowed_choices_cannot_retain_an_old_input_fingerprint():
    archive = report.payload(dict(inputs=flat().model_dump(mode="json")))
    archive["inputs"]["dimensions"][0]["locked_choice"] = "early"
    with pytest.raises(ValueError, match="fingerprint"):
        report.loads(encode(archive))


@pytest.mark.parametrize("raw,message", [(b"\xff", "UTF-8"), (b" " * (MAX_BYTES + 1), "2 MB")])
def test_import_rejects_bad_encoding_or_unbounded_inputs(raw, message):
    with pytest.raises(ValueError, match=message):
        report.loads(raw)


def test_bom_input_roundtrip_retains_money_and_original_policy_fingerprint():
    case = flat()
    restored = report.loads(b"\xef\xbb\xbf" + case.model_dump_json().encode())
    assert restored == case and fingerprint(restored) == fingerprint(case)
