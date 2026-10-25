"""JSON round-trips and atomic no-overwrite writes in an explicitly selected directory."""

import hashlib
import json
from decimal import Decimal
from pathlib import Path

from wealthlab.household.scenario import Scenario
from wealthlab.local_files import write_new

MAX_BYTES = 2_000_000
REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


def loads(raw: bytes | str) -> Scenario:
    data = raw.encode("utf-8") if isinstance(raw, str) else raw
    if len(data) > MAX_BYTES:
        raise ValueError("Scenario file exceeds the 2 MB input limit.")
    try:
        text = data.decode("utf-8-sig")
    except UnicodeDecodeError as error:
        raise ValueError("Use a UTF-8 JSON scenario file.") from error
    value = json.loads(text, parse_float=Decimal)
    if isinstance(value, dict) and value.get("format") == "wealthlab-household-projection-v1":
        scenario = Scenario.model_validate(value.get("inputs"))
        if value.get("input_sha256") != fingerprint(scenario):
            raise ValueError("Projection input fingerprint does not match the validated inputs.")
        return scenario
    return Scenario.model_validate(value)


def fingerprint(scenario: Scenario) -> str:
    return hashlib.sha256(scenario.model_dump_json().encode()).hexdigest()


def save_new(scenario: Scenario, directory: Path, filename: str) -> Path:
    return write_new(scenario.model_dump_json(indent=2), directory, filename, REPOSITORY_ROOT)
