"""Re-import recomputes a search rather than trusting archived outcomes or validation success."""

import pytest
from optimization_cases import flat

from wealthlab.household.report import encode
from wealthlab.optimization import report


def test_changed_allowed_choices_cannot_retain_an_old_input_fingerprint():
    archive = report.payload(dict(inputs=flat().model_dump(mode="json")))
    archive["inputs"]["dimensions"][0]["locked_choice"] = "early"
    with pytest.raises(ValueError, match="fingerprint"):
        report.loads(encode(archive))
