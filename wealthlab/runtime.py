"""Confine third-party caches and temporary project files to this repository."""

import os
from pathlib import Path


def configure() -> Path:
    root = Path(__file__).resolve().parents[1]
    paths = {
        "XDG_CACHE_HOME": ".cache",
        "MPLCONFIGDIR": ".cache/matplotlib",
        "NUMBA_CACHE_DIR": ".cache/numba",
        "TAXCALC_JIT_CACHE_DIR": ".cache/taxcalc",
        "TMPDIR": ".runtime/tmp",
    }
    for variable, relative in paths.items():
        path = root / relative
        path.mkdir(parents=True, exist_ok=True)
        os.environ[variable] = str(path)
    return root
