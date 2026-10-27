"""Independent seeds change the sample, never the financial assumptions or horizon.

Do not treat historical replay or a named stress frequency as an estimated
probability. They remain supported by the existing Markets workbench; this
first selection/validation layer uses Monte Carlo samples only.
"""


def validate_markets(case):
    if case.training.mode != "monte_carlo" or case.validation.mode != "monte_carlo":
        raise ValueError("Search and held-out validation require separate Monte Carlo batches.")
    if case.training.seed == case.validation.seed:
        raise ValueError("Training and validation seeds must differ.")
    left = case.training.model_dump(exclude={"seed", "paths"})
    right = case.validation.model_dump(exclude={"seed", "paths"})
    if left != right:
        raise ValueError(
            "Training and validation must use the same market assumptions and horizon."
        )
    if (case.household.start, case.household.end) != (case.training.start, case.training.end):
        raise ValueError("Household and search horizons must match exactly.")
