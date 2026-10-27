"""Native progress covers each phase and never changes the frozen policy or cash results."""

from copy import deepcopy

from optimization_robustness_cases import case

from wealthlab.optimization.inputs import PolicySearch
from wealthlab.optimization.search import search


def test_path_progress_reports_all_phases_without_changing_any_results():
    data = case().model_dump(mode="json")
    data["training"]["paths"] = 2
    data["validation"]["paths"] = 3
    data["robustness"] = {name: data["robustness"][name] for name in ("flat", "exit_lock")}
    scenario = PolicySearch.model_validate(data)
    original = deepcopy(scenario)
    expected = search(scenario)
    paths, candidates = [], []
    actual = search(
        scenario,
        lambda done, total: candidates.append((done, total)),
        path_progress=lambda phase, done, total: paths.append((phase, done, total)),
    )
    assert actual == expected
    assert scenario == original
    assert candidates == [(1, 2), (2, 2)]
    phases = {
        "Training candidate 1": 2,
        "Training candidate 2": 2,
        "Independent validation": 3,
        "Check flat (baseline)": 1,
        "Check flat (selected)": 1,
        "Check exit_lock (baseline)": 1,
        "Check exit_lock (selected)": 1,
    }
    assert paths == [
        (phase, done, total) for phase, total in phases.items() for done in range(total + 1)
    ]
