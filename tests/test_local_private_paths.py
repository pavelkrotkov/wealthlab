"""Checkout guards and exclusive saves prevent public or overwritten output.

All Git metadata and selected output directories are original synthetic fixtures
inside the test runtime. A real external private directory is never written.
"""

import pytest

from wealthlab.local_files import write_new


def test_private_save_is_utf8_exclusive_and_leaves_no_temporary_file(tmp_path):
    main = current = tmp_path / "public"
    main.mkdir()
    private = tmp_path / "private_selected"
    private.mkdir()
    target = write_new('{"name":"café"}', private, "result.json", current)
    assert target.read_bytes() == '{"name":"café"}'.encode()
    with pytest.raises(FileExistsError):
        write_new("changed", private, "result.json", current)
    assert list(private.iterdir()) == [target]
    assert list(main.glob("*.json")) == []
