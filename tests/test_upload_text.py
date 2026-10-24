"""Uploaded bytes become real editable text while byte limits and encoding remain explicit."""

from io import BytesIO

import pytest

from wealthlab.household.storage import MAX_BYTES
from wealthlab.ui.uploads import read


def test_utf8_bom_and_unicode_are_decoded_without_a_python_bytes_repr():
    assert read(BytesIO(b'\xef\xbb\xbf{"name":"caf\xc3\xa9"}')) == '{"name":"café"}'


@pytest.mark.parametrize(("raw", "message"), [(b"x" * (MAX_BYTES + 1), "2 MB"), (b"\xff", "UTF-8")])
def test_invalid_uploads_fail_before_the_editor(raw, message):
    with pytest.raises(ValueError, match=message):
        read(BytesIO(raw))
