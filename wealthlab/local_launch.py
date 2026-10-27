"""Launch the existing app from its own root with explicit loopback and telemetry settings."""

import subprocess
import sys
from pathlib import Path

from wealthlab.household.storage import MAX_MB

ROOT = Path(__file__).resolve().parents[1]


def command(port=8501):
    if not 1 <= port <= 65535:
        raise ValueError("Port must be between 1 and 65535.")
    return [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(ROOT / "app.py"),
        "--server.address=127.0.0.1",
        f"--server.port={port}",
        "--server.headless=true",
        "--browser.gatherUsageStats=false",
        f"--server.maxUploadSize={MAX_MB}",
    ]


def serve(port):
    return subprocess.run(command(port), cwd=ROOT, check=False).returncode
