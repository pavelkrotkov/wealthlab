"""A failed household submission must not resurrect an old financial result on rerun."""

import json
from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_unconfirmed_medicare_clears_old_household_projection():
    app = AppTest.from_file(
        Path(__file__).resolve().parents[1] / "app.py", default_timeout=90
    ).run()
    next(b for b in app.button if b.label == "Load synthetic Medicare household").click().run()
    app.button(key="FormSubmitter:household-Validate and project").click().run()
    had_results = bool(app.metric)
    editor = next(a for a in app.text_area if a.label.startswith("Medicare coverage"))
    payload = json.loads(str(editor.value))
    payload["case"]["complete_context"] = False
    editor.set_value(json.dumps(payload))
    app.button(key="FormSubmitter:household-Validate and project").click().run()
    assert (had_results, bool(app.error)) == (True, True)
    app.run()
    assert not app.exception
    assert not app.metric
