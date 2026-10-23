"""JSON round-trips and atomic no-overwrite writes in an explicitly selected directory."""

import hashlib
import os
from pathlib import Path
from tempfile import NamedTemporaryFile

from wealthlab.household.scenario import Scenario

MAX_BYTES = 2_000_000
REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


def loads(raw: bytes | str) -> Scenario:
    if len(raw) > MAX_BYTES:
        raise ValueError("Scenario file exceeds the 2 MB input limit.")
    return Scenario.model_validate_json(raw)


def fingerprint(scenario: Scenario) -> str:
    return hashlib.sha256(scenario.model_dump_json().encode()).hexdigest()


def save_new(scenario: Scenario, directory: Path, filename: str) -> Path:
    root = directory.expanduser().resolve(strict=True)
    if root.is_relative_to(REPOSITORY_ROOT):
        raise ValueError("Select a private directory outside the public code repository.")
    if Path(filename).name != filename or not filename.endswith(".json"):
        raise ValueError("Use a plain filename ending in .json.")
    target = root / filename
    temporary = None
    try:
        with NamedTemporaryFile(mode="w", dir=root, prefix=".wealthlab-", delete=False) as output:
            temporary = Path(output.name)
            output.write(scenario.model_dump_json(indent=2))
            output.flush()
            os.fsync(output.fileno())
        os.link(temporary, target)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    return target
