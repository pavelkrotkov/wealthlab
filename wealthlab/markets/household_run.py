"""Run policies on the same realized batch; never optimize with future path knowledge."""

from wealthlab.household.projection import project
from wealthlab.markets.household_compile import compile_marks
from wealthlab.markets.household_execution import Execution
from wealthlab.markets.household_report import aggregate, summarize
from wealthlab.markets.household_validation import validate


def run(scenario, batch, binding, indices=None, progress=None):
    indices = list(range(len(batch.mark_returns))) if indices is None else list(indices)
    if not indices or len(indices) != len(set(indices)):
        raise ValueError("Select unique path indices from the realized batch.")
    for index in indices:
        validate(scenario, batch, binding, index)
    outcomes, details = [], []
    for index in indices:
        case = compile_marks(scenario, batch, binding, index)
        rows = project(case, market=Execution(case, batch, binding, index))
        outcomes.append(summarize(case, rows, index))
        details.append(dict(path=index, rows=rows))
        if progress is not None:
            progress(len(outcomes), len(indices))
    return dict(
        batch_id=batch.metadata["batch_id"],
        indices=indices,
        household=scenario.model_dump(mode="json"),
        binding=binding.model_dump(mode="json"),
        aggregate=aggregate(scenario, batch, outcomes),
        outcomes=outcomes,
        details=details,
    )


def paired(left, right):
    if (left["batch_id"], left["indices"]) != (right["batch_id"], right["indices"]):
        raise ValueError("Paired household comparisons require the same batch and path indices.")
    return [
        dict(
            path=a["path"],
            funded_change=int(b["funded"]) - int(a["funded"]),
            real_wealth_change=b["ending_real_wealth"] - a["ending_real_wealth"],
            shortfall_change=b["funding_shortfall"] - a["funding_shortfall"],
        )
        for a, b in zip(left["outcomes"], right["outcomes"], strict=True)
    ]
