"""Atomic exclusive UTF-8 writes in an explicitly selected non-code directory.

Canonical paths protect symlink aliases and every checkout of the same repository.
A complete flushed file is linked to a new name; existing files and destination
symlinks cannot be overwritten. Temporary files stay in that selected directory.
"""

import os
import subprocess
from pathlib import Path
from tempfile import NamedTemporaryFile

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def code_roots(repository_root: Path) -> set[Path]:
    """A linked worktree must also protect the main checkout and sibling worktrees."""
    root = repository_root.resolve()
    marker = root / ".git"
    if not marker.exists() and not marker.is_symlink():
        return {root}
    roots = git_roots(root)
    # Git may report a separate metadata directory as its main worktree.
    # Without a checkout marker there, the real main location is unknown.
    if root not in roots or any(not (path / ".git").exists() for path in roots):
        raise ValueError("Cannot resolve code repository metadata safely.")
    return roots


def git_roots(root):
    """Ask Git for unquoted NUL-delimited checkout paths without ambient routing."""
    try:
        result = subprocess.run(
            ["git", "-C", str(root), "worktree", "list", "--porcelain", "-z"],
            check=True,
            capture_output=True,
            timeout=5,
            env={key: value for key, value in os.environ.items() if not key.startswith("GIT_")},
        )
    except (OSError, subprocess.SubprocessError) as error:
        raise ValueError("Cannot resolve code repository metadata safely.") from error
    return {
        Path(os.fsdecode(field.removeprefix(b"worktree "))).resolve()
        for field in result.stdout.split(b"\0")
        if field.startswith(b"worktree ")
    }


def write_new(text: str, directory: Path, filename: str, repository_root=None) -> Path:
    root = directory.expanduser().resolve(strict=True)
    if not root.is_dir():
        raise ValueError("Select an existing private directory.")
    if any(root.is_relative_to(code) for code in code_roots(repository_root or REPOSITORY_ROOT)):
        raise ValueError("Select a private directory outside every public code checkout.")
    if Path(filename).name != filename or not filename.endswith(".json"):
        raise ValueError("Use a plain filename ending in .json.")
    target, temporary = root / filename, None
    try:
        with NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=root, prefix=".wealthlab-", delete=False
        ) as output:
            temporary = Path(output.name)
            output.write(text)
            output.flush()
            os.fsync(output.fileno())
        os.link(temporary, target)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    return target
