"""Project and compare complete country inputs alongside ordinary household scenarios.

Country replay retains the original Spain/PR facts, not just a resolved bill.
The existing decoder, fingerprint, metadata, encoder and financial engines are
shared; archived ledger values are never inputs to a fresh calculation.
"""

from pathlib import Path

from wealthlab.household import report, storage
from wealthlab.household.projection import project
from wealthlab.tax.jurisdiction_execution import evaluate
from wealthlab.tax.jurisdiction_execution_facts import JurisdictionExecutionCase

FORMAT = "wealthlab-country-projection-v1"


def loads(raw):
    value = storage.decode(raw)
    if isinstance(value, dict) and value.get("format") == FORMAT:
        case = JurisdictionExecutionCase.model_validate(value.get("inputs"))
        if value.get("input_sha256") != storage.fingerprint(case):
            raise ValueError("Country input fingerprint does not match the validated inputs.")
        return case
    if isinstance(value, dict) and "scenario" in value:
        return JurisdictionExecutionCase.model_validate(value)
    return storage.from_value(value)


def household(case):
    return case.scenario if isinstance(case, JurisdictionExecutionCase) else case


def payload(case, result):
    return dict(
        report.payload(case.scenario, result["rows"]),
        format=FORMAT,
        inputs=case.model_dump(mode="json"),
        input_sha256=storage.fingerprint(case),
        country_assessments=result["country_assessments"],
        reconciliation=result["reconciliation"],
        limitations="Conditional country facts and shared cash; no automatic relocation search.",
    )


def calculate(case):
    if isinstance(case, JurisdictionExecutionCase):
        return payload(case, evaluate(case.scenario, spain=case.spain))
    return report.payload(case, project(case))


def read(path):
    with Path(path).expanduser().open("rb") as source:
        return loads(source.read(storage.MAX_BYTES + 1))


def run(path):
    return calculate(read(path))


def compare(baseline_path, candidate_path):
    return compare_inputs(read(baseline_path), read(candidate_path))


def compare_inputs(baseline, candidate):
    before, after = household(baseline), household(candidate)
    if (before.start, before.end) != (after.start, after.end):
        raise ValueError("Comparison dates must agree.")
    left, right = calculate(baseline), calculate(candidate)
    return dict(
        format="wealthlab-household-comparison-v1",
        baseline=left,
        candidate=right,
        ending_wealth_change_usd=right["months"][-1]["net_wealth"]
        - left["months"][-1]["net_wealth"],
        full_tax_optimization_supported=False,
    )
