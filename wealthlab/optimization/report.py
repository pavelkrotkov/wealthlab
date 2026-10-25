"""UI and CLI reproduce the same validated finite-grid calculation, never archived outcomes.

The input checksum detects edits, not legal correctness or source authenticity.
Report imports discard outcomes and execute a fresh search under current code.
Large reports may exceed the bounded input size; export the separate inputs then.
"""

import json
from decimal import Decimal
from pathlib import Path

from wealthlab.household.report import dependencies, revision
from wealthlab.household.storage import MAX_BYTES, fingerprint
from wealthlab.optimization.inputs import PolicySearch
from wealthlab.optimization.search import search

FORMAT = "wealthlab-policy-search-v1"


def loads(raw):
    data = raw.encode("utf-8") if isinstance(raw, str) else raw
    if len(data) > MAX_BYTES:
        raise ValueError(
            "Policy search exceeds the 2 MB input limit; use the separate input export."
        )
    try:
        text = data.decode("utf-8-sig")
    except UnicodeDecodeError as error:
        raise ValueError("Use a UTF-8 JSON policy search file.") from error
    value = json.loads(text, parse_float=Decimal)
    if isinstance(value, dict) and value.get("format") == FORMAT:
        case = PolicySearch.model_validate(value.get("inputs"))
        if value.get("input_sha256") != fingerprint(case):
            raise ValueError("Policy search fingerprint does not match its validated inputs.")
        return case
    return PolicySearch.model_validate(value)


def payload(result):
    case = PolicySearch.model_validate(result["inputs"])
    return dict(
        result,
        format=FORMAT,
        input_sha256=fingerprint(case),
        source_revision=revision(),
        dependencies=dependencies(),
        full_tax_optimization_supported=False,
    )


def run(path):
    with Path(path).expanduser().open("rb") as source:
        case = loads(source.read(MAX_BYTES + 1))
    return payload(search(case))
