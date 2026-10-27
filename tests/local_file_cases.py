"""Real synthetic Git repositories entirely inside the selected test runtime."""

import os
import subprocess


def git(*args):
    return subprocess.run(
        ["git", "-c", "core.hooksPath=/dev/null", *map(str, args)],
        check=True,
        capture_output=True,
        timeout=10,
        env={key: value for key, value in os.environ.items() if not key.startswith("GIT_")},
    )


def linked_checkouts(tmp_path, separate=False):
    main, current, sibling = (tmp_path / name for name in ("public", "current", "sibling"))
    options = ["--separate-git-dir", str(tmp_path / "metadata.git")] if separate else []
    git("init", "--template=", "--initial-branch=main", *options, main)
    git(
        "-C",
        main,
        "-c",
        "user.name=Synthetic",
        "-c",
        "user.email=example@example.invalid",
        "commit",
        "--allow-empty",
        "-m",
        "Synthetic fixture",
    )
    for root in (current, sibling):
        git("-C", main, "worktree", "add", "--detach", root)
    return main, current, sibling
