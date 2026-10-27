"""All scenario paths use bounded UTF-8 bytes, including BOM and multibyte input."""

import pytest

from wealthlab.household.example import synthetic
from wealthlab.household.storage import MAX_BYTES, fingerprint, loads


def test_utf8_bom_scenario_round_trip_preserves_the_exact_input_fingerprint():
    scenario = synthetic()
    assert fingerprint(loads(b"\xef\xbb\xbf" + scenario.model_dump_json().encode())) == fingerprint(
        scenario
    )


@pytest.mark.parametrize("raw", ["é" * (MAX_BYTES // 2 + 1), b"x" * (MAX_BYTES + 1)])
def test_input_limit_is_bytes_for_both_string_and_byte_callers(raw):
    with pytest.raises(ValueError, match="2 MB"):
        loads(raw)


def test_invalid_text_encoding_is_reported_without_raw_input_values():
    with pytest.raises(ValueError, match="UTF-8"):
        loads(b"\xff")
