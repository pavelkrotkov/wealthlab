"""Invalid eligibility, product identity and duplicate tax facts block before funding."""

import pytest

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.retirement.workplace_example import synthetic


@pytest.mark.parametrize(
    "field",
    ["complete_single_employer_elections_confirmed", "gross_wages_before_deferrals_confirmed"],
)
def test_missing_confirmation_blocks(field):
    s = synthetic()
    s = s.model_copy(update=dict(workplace_plan=s.workplace_plan.model_copy(update={field: False})))
    with pytest.raises(ValueError, match="Confirm"):
        project(s)


@pytest.mark.parametrize(
    "change,match",
    [
        ("years", "every calendar year"),
        ("duplicate", "unique"),
        ("owner", "contributing owner"),
        ("product", "match account products"),
        ("unresolved", "Resolve employee eligibility"),
        ("manual", "manual annual wage"),
    ],
)
def test_invalid_records_block(change, match):
    data = synthetic().model_dump(mode="json")
    plan = data["workplace_plan"]
    changes = dict(
        years=lambda: plan["years"].append(plan["years"][0].copy()),
        duplicate=lambda: plan["orders"].append(plan["orders"][0].copy()),
        owner=lambda: plan["orders"][0].update(owner="person_b"),
        product=lambda: plan["products"].pop("work_pretax"),
        unresolved=lambda: plan["years"][0]["contributors"][0].update(provenance="unresolved"),
        manual=lambda: data["tax_plan"]["cases"][0]["federal_income"].update(wages_primary="1"),
    )
    changes[change]()
    with pytest.raises(ValueError, match=match):
        project(Scenario.model_validate(data))
