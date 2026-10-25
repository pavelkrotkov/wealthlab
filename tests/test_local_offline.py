"""The selected synthetic household calculation makes no Python network connection."""

import socket
from pathlib import Path

from optimization_cases import flat

from wealthlab.household.report import run
from wealthlab.optimization import report as policy_report


def test_selected_household_projection_does_not_open_network_connections(monkeypatch):
    def deny(*args, **kwargs):
        raise AssertionError("Household calculation attempted an implicit network connection.")

    monkeypatch.setattr(socket.socket, "connect", deny)
    result = run(Path(__file__).resolve().parents[1] / "examples/synthetic.json")
    assert result["months"][-1]["net_wealth"] == 224000


def test_actual_optimizer_does_not_open_a_network_connection(tmp_path, monkeypatch):
    source = tmp_path / "case.json"
    source.write_text(flat().model_dump_json())

    def deny(*args, **kwargs):
        raise AssertionError("Optimizer attempted an implicit network connection")

    monkeypatch.setattr(socket.socket, "connect", deny)
    result = policy_report.run(source)
    assert result["selection"] == "candidate_1"
    assert result["format"] == policy_report.FORMAT
