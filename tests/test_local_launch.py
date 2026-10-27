"""Native loopback launch has no shell interpolation or caller-directory configuration drift."""

from types import SimpleNamespace
from unittest.mock import patch

import pytest

from wealthlab.local_launch import ROOT, command, serve


def test_launch_always_selects_explicit_loopback_privacy_and_upload_limits():
    args = command(8502)
    assert "--server.address=127.0.0.1" in args
    assert "--browser.gatherUsageStats=false" in args
    assert "--server.maxUploadSize=200" in args
    assert str(ROOT / "app.py") in args
    with patch(
        "wealthlab.local_launch.subprocess.run", return_value=SimpleNamespace(returncode=0)
    ) as run:
        assert serve(8502) == 0
    assert run.call_args.kwargs["cwd"] == ROOT


@pytest.mark.parametrize("port", [0, 65536])
def test_invalid_ports_cannot_start_a_server(port):
    with pytest.raises(ValueError, match="Port"):
        command(port)
