"""Enforce metrics on every first-party Python file discovered through Git."""

import json
import subprocess
import sys
from pathlib import Path

from tools.quality_metrics import LIMITS, measure, violations


def python_files(root: Path) -> list[Path]:
    """Git's ignore rules exclude environments; every owned Python path counts."""
    result = subprocess.run(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard", "*.py"],
        cwd=root,
        check=True,
        capture_output=True,
    )
    names = result.stdout.decode().split("\0")
    return sorted({root / name for name in names if name})


def audit(root: Path) -> tuple[list[dict], list[str]]:
    reports, failures = [], []
    for path in python_files(root):
        name = str(path.relative_to(root))
        try:
            metrics = measure(path.read_text(encoding="utf-8"))
        except (SyntaxError, UnicodeError, OSError) as error:
            failures.append(f"{name}: {error}")
            continue
        reports.append({"path": name, **metrics})
        failures.extend(f"{name}: {error}" for error in violations(metrics))
    if not reports:
        failures.append("No readable first-party Python files found")
    return reports, failures


def main() -> int:
    reports, failures = audit(Path(__file__).resolve().parents[1])
    print(json.dumps({"limits": LIMITS, "files": reports, "failures": failures}, indent=2))
    return int(bool(failures))


if __name__ == "__main__":
    sys.exit(main())
