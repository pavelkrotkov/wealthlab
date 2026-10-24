"""Reject inconsistent work states and non-wage targets before changing household income."""

from wealthlab.tax.projection_validation import validate as validate_tax


def validate(scenario):
    if scenario.tax_plan is None:
        raise ValueError("Employment wage paths require an explicit household tax plan.")
    validate_tax(scenario.tax_plan, scenario)
    paths = scenario.employment_plan.paths
    validate_records(paths)
    validate_unique_targets(paths)
    incomes = {i.id: i for i in scenario.incomes}
    rules = {r.income_id: r for r in scenario.tax_plan.income_rules}
    for path in paths:
        validate_targets(path, incomes, rules)
        validate_changes(path, scenario)


def validate_records(paths):
    records = [*paths, *(e for path in paths for e in path.changes)]
    identifiers = [r.id for r in records]
    if len(identifiers) != len(set(identifiers)):
        raise ValueError("Employment path and change IDs must be unique.")
    if any(r.provenance == "unresolved" for r in records):
        raise ValueError("Resolve employment path assumptions before projecting.")


def validate_unique_targets(paths):
    targets = [identifier for p in paths for identifier in p.income_ids]
    if len(targets) != len(set(targets)):
        raise ValueError("A wage stream can belong to only one employment path.")


def validate_targets(path, incomes, rules):
    for identifier in path.income_ids:
        income = incomes.get(identifier)
        if income is None or income.owner != path.owner:
            raise ValueError("Employment targets must be known income streams owned by the worker.")
        rule = rules[identifier]
        if rule.federal not in {"wages_primary", "wages_spouse"} or rule.new_jersey != "wages":
            raise ValueError("This employment layer supports federal/NJ wage streams only.")


def validate_changes(path, scenario):
    dates = [e.date for e in path.changes]
    if len(dates) != len(set(dates)):
        raise ValueError("Supply one work-state change per path and date.")
    active = path.opening_multiplier > 0
    for change in sorted(path.changes, key=lambda e: e.date):
        if not scenario.start <= change.date < scenario.end:
            raise ValueError("Work-state changes must fall inside the household projection.")
        validate_transition(change, active)
        active = change.multiplier > 0


def validate_transition(change, active):
    # Explicit state transitions avoid treating a second job loss as another pay
    # reduction or permitting a return-to-work while the job is still active.
    expected = {
        "job_loss": (True, False),
        "return_to_work": (False, True),
        "pay_change": (True, True),
    }
    if (active, change.multiplier > 0) != expected[change.kind]:
        raise ValueError(f"Inconsistent {change.kind} work state or pay multiplier.")
