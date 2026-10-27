"""Enumerate the allowed finite grid; select once before opening held-out results."""

from itertools import product

from wealthlab.markets.household_run import run
from wealthlab.markets.paths import generate
from wealthlab.optimization.assessment import assess, score
from wealthlab.optimization.compile import compile_candidate
from wealthlab.optimization.progress import observe
from wealthlab.optimization.robustness import check_all, validation_passed
from wealthlab.optimization.sleeve_allocations import audit as allocation_audit
from wealthlab.optimization.validation import choices, validate


def search(case, progress=None, *, path_progress=None):
    count = validate(case)
    training = generate(case.training)
    evaluated, winner = [], None
    # ponytail: finite menus use itertools; add a proposal solver only if grids become too costly.
    grid = product(*(choices(d) for d in case.dimensions))
    for index, selection in enumerate(grid):
        candidate, details = evaluate(case, selection, index, training, path_progress)
        evaluated.append(candidate)
        if improves(candidate, winner):
            winner = (candidate, selection, details)
        if progress is not None:
            progress(index + 1, count)
    # Validation cannot choose a different candidate, even when the selected
    # policy fails. Preserve the unsuccessful validation as an actual result.
    held_out = validate_winner(case, winner, path_progress)
    robustness = check_all(case, winner, path_progress)
    return dict(
        inputs=case.model_dump(mode="json"),
        status="best_evaluated_candidate" if winner else "no_feasible_evaluated_candidate",
        grid_candidates=count,
        evaluated_candidates=len(evaluated),
        solver="exhaustive_finite_user_choices",
        global_optimum_claim=False,
        selection=winner[0]["candidate"] if winner else None,
        candidates=evaluated,
        training_batch=training.export(),
        selected_training=winner[2] if winner else None,
        held_out=held_out,
        robustness=robustness,
        configured_validation_passed=validation_passed(held_out, robustness),
    )


def evaluate(case, selection, index, batch, path_progress=None):
    identity = dict(
        candidate=f"candidate_{index}",
        choices={d.id: c.id for d, c in zip(case.dimensions, selection, strict=True)},
    )
    try:
        household, binding = compile_candidate(case, selection)
        result = run(
            household,
            batch,
            binding,
            progress=observe(path_progress, f"Training candidate {index + 1}", batch),
        )
    except ValueError as error:
        return dict(**identity, eligible=False, unsupported_reason=str(error)), None
    return dict(
        **identity,
        **assess(case, household, result),
        opening_allocation_audit=allocation_audit(case.household, household),
    ), result


def improves(candidate, winner):
    return candidate.get("eligible", False) and (
        winner is None or score(candidate) > score(winner[0])
    )


def validate_winner(case, winner, path_progress=None):
    if winner is None:
        return None
    candidate, selection, _ = winner
    batch = generate(case.validation)
    household, binding = compile_candidate(case, selection)
    try:
        result = run(
            household,
            batch,
            binding,
            progress=observe(path_progress, "Independent validation", batch),
        )
    except ValueError as error:
        return dict(
            selected_candidate=candidate["candidate"],
            batch=batch.export(),
            results=None,
            assessment=dict(eligible=False, unsupported_reason=str(error)),
        )
    return dict(
        selected_candidate=candidate["candidate"],
        assessment=assess(case, household, result),
        batch=batch.export(),
        results=result,
    )
