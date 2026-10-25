"""Shared UI/CLI payloads preserve exact inputs and full existing ledger rows.

Date and Decimal values have explicit lossless representations. An unknown
structured audit or nonfinite amount must fail rather than become a repr string
that looks like a successfully preserved financial record.
"""

import json
import subprocess
from datetime import date
from decimal import Decimal
from importlib.metadata import version
from pathlib import Path

from wealthlab.household.projection import project
from wealthlab.household.storage import MAX_BYTES, fingerprint, loads

ROOT = Path(__file__).resolve().parents[2]


def revision():
    """Git is optional at runtime; an unavailable revision is explicit, never fabricated."""
    try:
        head = subprocess.run(
            ["git", "rev-parse", "--verify", "HEAD"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
            timeout=5,
        ).stdout.strip()
        status = subprocess.run(
            ["git", "status", "--porcelain", "--untracked-files=normal"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
            timeout=5,
        ).stdout
        return dict(head=head, dirty=bool(status))
    except (OSError, subprocess.SubprocessError):
        return dict(head=None, dirty=None)


def payload(scenario, rows):
    return dict(
        format="wealthlab-household-projection-v1",
        synthetic=scenario.synthetic,
        input_sha256=fingerprint(scenario),
        source_revision=revision(),
        dependencies={
            name: version(name)
            for name in ("numpy", "pydantic", "taxcalc", "QuantLib", "streamlit")
        },
        taxes_modeled=scenario.tax_plan is not None,
        inputs=scenario.model_dump(mode="json"),
        months=rows,
        limitations="Conditional enabled plans only; no full-tax optimization certificate.",
    )


def encode(report):
    return json.dumps(report, indent=2, default=json_value, allow_nan=False) + "\n"


def json_value(value):
    if isinstance(value, Decimal):
        if not value.is_finite():
            raise ValueError("Report amounts must be finite.")
        return str(value)
    if isinstance(value, date):
        return value.isoformat()
    raise ValueError("Unsupported structured report value; no audit was flattened.")


def read_scenario(path):
    with Path(path).expanduser().open("rb") as source:
        return loads(source.read(MAX_BYTES + 1))


def run(path):
    scenario = read_scenario(path)
    return payload(scenario, project(scenario))


def compare(baseline_path, candidate_path):
    baseline, candidate = read_scenario(baseline_path), read_scenario(candidate_path)
    if (baseline.start, baseline.end) != (candidate.start, candidate.end):
        raise ValueError("Comparison dates must agree.")
    before, after = project(baseline), project(candidate)
    return dict(
        format="wealthlab-household-comparison-v1",
        baseline=payload(baseline, before),
        candidate=payload(candidate, after),
        ending_wealth_change_usd=after[-1]["net_wealth"] - before[-1]["net_wealth"],
        full_tax_optimization_supported=False,
    )
