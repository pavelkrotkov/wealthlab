"""Uploaded bytes become real editable text while byte limits and encoding remain explicit."""

from io import BytesIO

import pytest

from wealthlab.ui.uploads import read


def test_utf8_bom_and_unicode_are_decoded_without_a_python_bytes_repr():
    assert read(BytesIO(b'\xef\xbb\xbf{"name":"caf\xc3\xa9"}')) == '{"name":"café"}'


def test_invalid_uploads_fail_before_the_editor():
    raw, message = b"\xff", "UTF-8"
    with pytest.raises(ValueError, match=message):
        read(BytesIO(raw))
