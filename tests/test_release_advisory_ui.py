"""Visible and imported UI reports retain the native finite structured JSON contract.

Archived outcomes may be edited independently from their unchanged source
fingerprint. Re-execution must recover actual paid fees and dated NJ loss carry
rather than consume archived wealth, zero costs or an asserted successful exit.
"""

import json

from test_local_cli import invoke

from tests.release_advisory_cases import matched as matched
from wealthlab.household.report import encode


def test_visible_optimizer_audit_uses_the_same_structured_finite_encoder(matched):
    _, result, app, _ = matched
    text = next(item.value for item in app.json if '"input_sha256"' in item.value)
    visible = json.loads(text)
    assert visible == result
    assert "BusinessLoss(" not in text and "Decimal(" not in text


def test_imported_cli_audit_reexecutes_fees_and_nj_losses_instead_of_forged_outcomes(
    matched, tmp_path
):
    _, original, app, _ = matched
    archive = json.loads(encode(original))
    archive.update(selection="forged_free_contract", candidates=[])
    row = archive["selected_training"]["details"][0]["rows"][-1]
    row.update(closing_cash="999999999", advisory_fees_paid="0", advisory_fees_owed="0")
    row["annual_tax"]["new_jersey"]["business_carry"] = []
    source = tmp_path / "synthetic-forged-outcomes.json"
    source.write_text(encode(archive), encoding="utf-8")
    process = invoke(["optimize", str(source)], tmp_path)
    assert process.returncode == 0, process.stderr
    assert json.loads(process.stdout) == original
    app.text_area("policy_search_editor").set_value(source.read_text())
    app.button(key="FormSubmitter:policy_search-Search allowed policies").click().run()
    assert not app.exception and not app.error
    assert json.loads(encode(app.session_state["policy_search_result"])) == original
    assert sorted(p.name for p in tmp_path.iterdir()) == [source.name]
