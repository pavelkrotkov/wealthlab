"""Checkout guards and exclusive saves prevent public or overwritten output.

All Git metadata and selected output directories are original synthetic fixtures
inside the test runtime. A real external private directory is never written.
"""

import pytest
from local_file_cases import linked_checkouts

from wealthlab.local_files import code_roots, write_new


def test_all_linked_code_roots_and_symlink_aliases_are_protected(tmp_path):
    main, current, sibling = linked_checkouts(tmp_path)
    assert code_roots(current) == {main, current, sibling}
    alias = tmp_path / "selected_alias"
    alias.symlink_to(sibling, target_is_directory=True)
    for directory in (main, current, sibling, alias):
        with pytest.raises(ValueError, match="outside every"):
            write_new("{}", directory, "result.json", current)


def test_private_save_is_utf8_exclusive_and_leaves_no_temporary_file(tmp_path):
    main, current, _ = linked_checkouts(tmp_path)
    private = tmp_path / "private_selected"
    private.mkdir()
    target = write_new('{"name":"café"}', private, "result.json", current)
    assert target.read_bytes() == '{"name":"café"}'.encode()
    with pytest.raises(FileExistsError):
        write_new("changed", private, "result.json", current)
    assert list(private.iterdir()) == [target]
    assert list(main.glob("*.json")) == []


def test_existing_destination_symlink_cannot_overwrite_its_target(tmp_path):
    _, current, _ = linked_checkouts(tmp_path)
    private = tmp_path / "private_selected"
    private.mkdir()
    original = private / "original.json"
    original.write_text("original", encoding="utf-8")
    (private / "result.json").symlink_to(original)
    with pytest.raises(FileExistsError):
        write_new("replacement", private, "result.json", current)
    assert original.read_text() == "original"
    assert not list(private.glob(".wealthlab-*"))


def test_selected_output_requires_a_directory_and_resolvable_code_metadata(tmp_path):
    _, current, _ = linked_checkouts(tmp_path)
    selected_file = tmp_path / "not_a_directory"
    selected_file.touch()
    with pytest.raises(ValueError, match="existing private directory"):
        write_new("{}", selected_file, "result.json", current)
    (current / ".git").write_text("unrecognized metadata", encoding="utf-8")
    with pytest.raises(ValueError, match="metadata safely"):
        write_new("{}", tmp_path, "result.json", current)
