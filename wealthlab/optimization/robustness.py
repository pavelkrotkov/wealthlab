"""Replay baseline and frozen choice on one realized batch per named check.

Named adverse paths are not observations of event frequency. A stochastic
stress interval describes sampling conditional on that supplied overlay only.
Required failures affect validation, never the original training selection.
"""

from wealthlab.markets.household_run import paired, run
from wealthlab.markets.paths import generate
from wealthlab.optimization.assessment import assess
from wealthlab.optimization.compile import compile_candidate
from wealthlab.optimization.progress import observe


def check_all(case, winner, path_progress=None):
    if winner is None:
        return {
            name: dict(status="not_run_no_training_candidate", required=item.required)
            for name, item in case.robustness.items()
        }
    candidate, selection, _ = winner
    selected = compile_candidate(case, selection)
    baseline = compile_candidate(case, [])
    return {
        name: check(case, item, candidate["candidate"], baseline, selected, name, path_progress)
        for name, item in case.robustness.items()
    }


def check(case, item, identity, baseline, selected, name="scenario", path_progress=None):
    batch = generate(item.market)
    reference = replay(
        case,
        baseline,
        batch,
        item.market.stochastic,
        observe(path_progress, f"Check {name} (baseline)", batch),
    )
    frozen = replay(
        case,
        selected,
        batch,
        item.market.stochastic,
        observe(path_progress, f"Check {name} (selected)", batch),
    )
    supported = reference["results"] is not None and frozen["results"] is not None
    status = outcome_status(supported, frozen)
    return dict(
        selected_candidate=identity,
        required=item.required,
        status=status,
        mode=item.market.mode,
        sampling_scope="conditional_on_named_stress" if item.market.stochastic else "supplied_path",
        batch=batch.export(),
        baseline=reference,
        selected=frozen,
        paired_changes=paired(reference["results"], frozen["results"]) if supported else None,
    )


def replay(case, inputs, batch, sampled, progress=None):
    household, binding = inputs
    try:
        result = run(household, batch, binding, progress=progress, country=case.country_context)
    except ValueError as error:
        return dict(results=None, assessment=dict(eligible=False), unsupported_reason=str(error))
    return dict(results=result, assessment=assess(case, household, result, sampled=sampled))


def outcome_status(supported, selected):
    if not supported:
        return "unsupported"
    return "passed" if selected["assessment"]["eligible"] else "failed"


def validation_passed(held_out, checks):
    if held_out is None:
        return None
    return held_out["assessment"]["eligible"] and all(
        item["status"] == "passed" for item in checks.values() if item["required"]
    )
