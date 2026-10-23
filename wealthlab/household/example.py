"""Load the deliberately synthetic starter, with no private source dependencies."""

from pathlib import Path

from wealthlab.household.storage import loads


def synthetic():
    path = Path(__file__).resolve().parents[2] / "examples" / "synthetic.json"
    return loads(path.read_bytes())
