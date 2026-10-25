"""Atomic exclusive UTF-8 writes in an explicitly selected non-code directory.

Canonical paths protect symlink aliases and every checkout of the same repository.
A complete flushed file is linked to a new name; existing files and destination
symlinks cannot be overwritten. Temporary files stay in that selected directory.
"""

import os
from pathlib import Path
from tempfile import NamedTemporaryFile

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def code_roots(repository_root: Path) -> set[Path]:
    """A linked worktree must also protect the main checkout and sibling worktrees."""
    root = repository_root.resolve()
    roots = {root}
    marker = root / ".git"
    common = marker
    if marker.is_file():
        text = marker.read_text(encoding="utf-8").strip()
        if not text.startswith("gitdir: "):
            raise ValueError("Cannot resolve code repository metadata safely.")
        gitdir = (root / text.removeprefix("gitdir: ")).resolve()
        common = (gitdir / (gitdir / "commondir").read_text(encoding="utf-8").strip()).resolve()
        if common.name == ".git":
            roots.add(common.parent)
    for pointer in (common / "worktrees").glob("*/gitdir"):
        roots.add(Path(pointer.read_text(encoding="utf-8").strip()).parent.resolve())
    return roots


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
