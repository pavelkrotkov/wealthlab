"""Actual Git discovery protects unconventional checkout names and fails closed."""

import subprocess
from unittest.mock import patch

import pytest
from local_file_cases import linked_checkouts

from wealthlab.local_files import code_roots, write_new


def test_unlocatable_separate_main_fails_closed_from_every_checkout(tmp_path):
    roots = linked_checkouts(tmp_path, separate=True)
    for current in roots:
        for destination in (*roots, tmp_path):
            with pytest.raises(ValueError, match="metadata safely"):
                write_new("{}", destination, "private.json", current)
            assert not (destination / "private.json").exists()


def test_git_environment_cannot_redirect_repository_discovery(tmp_path, monkeypatch):
    main, current, sibling = linked_checkouts(tmp_path)
    unrelated = tmp_path / "unrelated"
    unrelated.mkdir()
    monkeypatch.setenv("GIT_DIR", str(unrelated))
    monkeypatch.setenv("GIT_WORK_TREE", str(unrelated))
    assert code_roots(current) == {main, current, sibling}


@pytest.mark.parametrize("failure", [FileNotFoundError(), subprocess.TimeoutExpired("git", 5)])
def test_unavailable_git_never_falls_back_to_incomplete_roots(tmp_path, failure):
    _, current, _ = linked_checkouts(tmp_path)
    with (
        patch("wealthlab.local_files.subprocess.run", side_effect=failure),
        pytest.raises(ValueError, match="metadata safely"),
    ):
        write_new("{}", tmp_path, "private.json", current)
    assert not (tmp_path / "private.json").exists()


def test_missing_current_root_in_git_output_fails_closed(tmp_path):
    _, current, _ = linked_checkouts(tmp_path)
    result = subprocess.CompletedProcess([], 0, stdout=b"worktree /unrelated\0\0")
    with (
        patch("wealthlab.local_files.subprocess.run", return_value=result),
        pytest.raises(ValueError, match="metadata safely"),
    ):
        code_roots(current)


def test_installed_copy_without_git_still_protects_its_code_directory(tmp_path):
    assert code_roots(tmp_path) == {tmp_path}
    with pytest.raises(ValueError, match="outside every"):
        write_new("{}", tmp_path, "private.json", tmp_path)
