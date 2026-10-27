"""Original monthly advance charges use actual opening snapshots, never a named adviser quote."""

from datetime import timedelta
from itertools import pairwise

from wealthlab.household.advisory_example import plan
from wealthlab.household.advisory_inputs import AdvisoryPlan
from wealthlab.household.calendar import months
from wealthlab.household.example import synthetic as household


def advance_plan(scenario):
    periods = list(months(scenario.start, scenario.end))
    if len(periods) < 2:
        raise ValueError("The advance starter requires at least two modeled months.")
    data = plan(scenario).model_dump(mode="json")
    data["valuation_timing"] = "explicit_observed_snapshot_cutoffs"
    schedule = data["schedules"][0]
    schedule["covered"].extend(
        dict(account_id=a.id, value_basis="modeled_net_account_equity")
        for a in scenario.accounts
        if a.wrapper in {"hsa", "education"}
    )
    schedule.update(
        source_ref=(
            "Original hypothetical nonrefundable monthly advance schedule for services from "
            "the second modeled month through the horizon; no first-month service charge"
        ),
        advance_nonrefundable_no_proration_assumed_confirmed=True,
        periods=[
            dict(
                accrual_start=following_start,
                accrual_end=following_end,
                valuation_date=start,
                valuation_cutoff="opening",
                assessment_date=end - timedelta(days=1),
                payment_due_date=end - timedelta(days=1),
            )
            for (start, end), (following_start, following_end) in pairwise(periods)
        ],
    )
    return AdvisoryPlan.model_validate(data)


def synthetic():
    case = household()
    return case.model_copy(
        update=dict(
            name="Synthetic observed-opening monthly advance advisory fees",
            advisory_fee_plan=advance_plan(case),
        )
    )
