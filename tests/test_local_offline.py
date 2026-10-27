"""The selected synthetic household calculation makes no Python network connection."""

import socket
from pathlib import Path

from wealthlab.household.report import run


def test_selected_household_projection_does_not_open_network_connections(monkeypatch):
    def deny(*args, **kwargs):
        raise AssertionError("Household calculation attempted an implicit network connection.")

    monkeypatch.setattr(socket.socket, "connect", deny)
    result = run(Path(__file__).resolve().parents[1] / "examples/synthetic.json")
    assert result["months"][-1]["net_wealth"] == 224000
