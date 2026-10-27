"""Private saves are atomic, exclusive and reproducible; malformed imports fail."""

import pytest

from wealthlab.household import storage
from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario


def test_round_trip_and_no_overwrite(payload, tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "REPOSITORY_ROOT", tmp_path / "public")
    scenario = Scenario.model_validate(payload)
    target = storage.save_new(scenario, tmp_path, "private.json")
    restored = storage.loads(target.read_bytes())
    assert project(restored) == project(scenario)
    assert storage.fingerprint(restored) == storage.fingerprint(scenario)
    with pytest.raises(FileExistsError):
        storage.save_new(scenario, tmp_path, "private.json")
    assert list(tmp_path.iterdir()) == [target]


def test_public_repo_and_path_traversal_rejected(payload, tmp_path, monkeypatch):
    scenario = Scenario.model_validate(payload)
    monkeypatch.setattr(storage, "REPOSITORY_ROOT", tmp_path)
    with pytest.raises(ValueError, match="outside"):
        storage.save_new(scenario, tmp_path, "scenario.json")
    monkeypatch.setattr(storage, "REPOSITORY_ROOT", tmp_path / "public")
    with pytest.raises(ValueError, match="plain filename"):
        storage.save_new(scenario, tmp_path, "../scenario.json")


def test_bad_imports(monkeypatch):
    with pytest.raises(ValueError):
        storage.loads(b'{"schema_version": 1}')
    monkeypatch.setattr(storage, "MAX_BYTES", 10)
    with pytest.raises(ValueError, match="200 MB"):
        storage.loads(b" " * 11)
