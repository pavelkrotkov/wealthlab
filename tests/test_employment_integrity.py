"""A salary stream is transformed once; work state never duplicates cash or identifiers."""

import pytest

from wealthlab.employment.example import synthetic
from wealthlab.employment.wages import prepare


def test_duplicate_work_records_and_duplicate_target_streams_are_rejected():
    case = synthetic()
    path = case.employment_plan.paths[0]
    duplicate = path.model_copy(update=dict(id="another_path", changes=[]))
    plan = case.employment_plan.model_copy(update=dict(paths=[path, duplicate]))
    with pytest.raises(ValueError, match="only one employment path"):
        prepare(case.model_copy(update=dict(employment_plan=plan)))
    first = path.changes[0].model_copy(update=dict(id=path.id))
    path = path.model_copy(update=dict(changes=[first, path.changes[1]]))
    plan = case.employment_plan.model_copy(update=dict(paths=[path]))
    with pytest.raises(ValueError, match="IDs must be unique"):
        prepare(case.model_copy(update=dict(employment_plan=plan)))
