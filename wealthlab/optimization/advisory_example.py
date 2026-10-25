"""Original common marginal fees cover current and optional native strategy accounts explicitly."""

from wealthlab.household.advisory_example import plan
from wealthlab.optimization.advisory_fees import offered_accounts
from wealthlab.optimization.inputs import PolicySearch


def extend(case):
    if not case.household.synthetic or case.household.advisory_fee_plan is not None:
        raise ValueError(
            "The advisory starter requires a synthetic case without an existing fee plan."
        )
    data = case.model_dump(mode="json")
    schedule_plan = plan(case.household).model_dump(mode="json")
    schedule = schedule_plan["schedules"][0]
    present = {a.id for a in case.household.accounts}
    covered = {row["account_id"] for row in schedule["covered"]}
    for account_id, bases in offered_accounts(case):
        if account_id not in covered:
            schedule["covered"].append(coverage(account_id, bases, present))
            covered.add(account_id)
    schedule["source_ref"] = (
        "Original hypothetical common marginal advisory contract, including source-confirmed "
        "optional native strategy account coverage; no actual adviser quote"
    )
    data["household"]["advisory_fee_plan"] = schedule_plan
    return PolicySearch.model_validate(data)


def coverage(account_id, bases, present):
    basis = (
        "life_net_surrender_value"
        if "life_net_surrender_value" in bases
        else "modeled_net_account_equity"
    )
    return dict(
        account_id=account_id,
        value_basis=basis,
        presence="required" if account_id in present else "if_present",
        absence_permitted_by_source_confirmed=account_id not in present,
    )
