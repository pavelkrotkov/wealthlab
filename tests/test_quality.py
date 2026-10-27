"""Exercise discovery and failure handling using temporary real Git repositories."""

import subprocess
from pathlib import Path

from tools.quality import audit, python_files


def init_repo(path: Path):
    subprocess.run(["git", "init", "-q", str(path)], check=True)
    (path / ".gitignore").write_text(".venv/\n")


def test_discovery_includes_root_code_but_ignores_environment(tmp_path):
    init_repo(tmp_path)
    (tmp_path / "app.py").write_text("x = 1\n")
    (tmp_path / ".venv").mkdir()
    (tmp_path / ".venv" / "vendor.py").write_text("bad syntax")
    assert python_files(tmp_path) == [tmp_path / "app.py"]
    reports, failures = audit(tmp_path)
    assert len(reports) == 1
    assert not failures


def test_invalid_file_and_empty_repo_fail(tmp_path):
    init_repo(tmp_path)
    assert audit(tmp_path)[1] == ["No readable first-party Python files found"]
    (tmp_path / "broken.py").write_text("def broken(:")
    assert any("broken.py" in failure for failure in audit(tmp_path)[1])
