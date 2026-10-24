"""Bad work transitions and unsupported tax targets cannot reach household calculations."""

from datetime import date

import pytest

from wealthlab.employment.example import synthetic
from wealthlab.employment.wages import prepare
from wealthlab.tax.projection_inputs import IncomeRule


@pytest.mark.parametrize(
    ("kind", "multiplier"), [("job_loss", 1), ("return_to_work", 1), ("pay_change", 0)]
)
def test_inconsistent_initial_work_changes_are_rejected(kind, multiplier):
    case = synthetic()
    path = case.employment_plan.paths[0]
    change = path.changes[0].model_copy(update=dict(kind=kind, multiplier=multiplier))
    path = path.model_copy(update=dict(changes=[change]))
    plan = case.employment_plan.model_copy(update=dict(paths=[path]))
    with pytest.raises(ValueError, match="work state or pay multiplier"):
        prepare(case.model_copy(update=dict(employment_plan=plan)))


@pytest.mark.parametrize("field", ["owner", "income_ids", "provenance"])
def test_unresolved_or_mismatched_targets_block_projection(field):
    case = synthetic()
    changes = dict(owner="missing", income_ids=["missing"], provenance="unresolved")
    path = case.employment_plan.paths[0].model_copy(update={field: changes[field]})
    plan = case.employment_plan.model_copy(update=dict(paths=[path]))
    with pytest.raises(ValueError):
        prepare(case.model_copy(update=dict(employment_plan=plan)))


def test_missing_tax_context_and_non_wage_character_are_rejected():
    case = synthetic()
    with pytest.raises(ValueError, match="tax plan"):
        prepare(case.model_copy(update=dict(tax_plan=None)))
    rule = IncomeRule(income_id="salary", federal="interest", new_jersey="interest")
    tax = case.tax_plan.model_copy(update=dict(income_rules=[rule]))
    with pytest.raises(ValueError, match="wage streams only"):
        prepare(case.model_copy(update=dict(tax_plan=tax)))


def test_duplicate_dates_and_out_of_horizon_changes_are_rejected():
    case = synthetic()
    path = case.employment_plan.paths[0]
    for when in (path.changes[1].date, date(2029, 1, 1)):
        first = path.changes[0].model_copy(update=dict(date=when))
        changed = path.model_copy(update=dict(changes=[first, path.changes[1]]))
        plan = case.employment_plan.model_copy(update=dict(paths=[changed]))
        with pytest.raises(ValueError):
            prepare(case.model_copy(update=dict(employment_plan=plan)))
