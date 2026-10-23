"""A staged deletion is removed from Git's index, so it must not be audited."""

import subprocess

from tools.quality import audit, python_files


def test_git_rm_removes_staged_path(tmp_path):
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    for name in ("keep.py", "remove.py"):
        (tmp_path / name).write_text("x = 1\n")
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True)
    subprocess.run(["git", "rm", "-f", "remove.py"], cwd=tmp_path, check=True)
    assert python_files(tmp_path) == [tmp_path / "keep.py"]
    assert audit(tmp_path)[1] == []
