"""Changing funding does not authorize unchanged illustrated values or invented guarantees."""

from wealthlab.products.life_illustration_flows import debt


def validate(case):
    validate_dates(case)
    validate_records(case)
    validate_stop(case)
    # An incomplete history cannot establish an opening loan balance of zero.
    if case.complete_history_from_issue_confirmed:
        debt(case.flows)


def validate_dates(case):
    dates = [row.date for row in case.values]
    flow_dates = [row.date for row in case.flows]
    if dates != sorted(set(dates)) or flow_dates != sorted(flow_dates):
        raise ValueError("Value dates must be unique/ordered; cash flows must be in dated order.")
    # Equal dates are allowed for flows: the supplied order determines loan repayment.
    all_dates = [*dates, *flow_dates]
    if min(all_dates) < case.issue_date or max(all_dates) > dates[-1]:
        raise ValueError(
            "Flows and values must fall within the supplied issue-to-last-value horizon."
        )


def validate_records(case):
    records = [case, *case.flows]
    if any(row.provenance == "unresolved" for row in records):
        raise ValueError("Resolve critical policy/cash-flow assumptions before calculating.")
    ids = [row.id for row in case.flows]
    if len(ids) != len(set(ids)):
        raise ValueError("Cash-flow IDs must be unique within an illustration.")


def validate_stop(case):
    if case.stop_funding_date is None:
        return
    if case.stop_funding_date < case.issue_date:
        raise ValueError("The premium stop date cannot precede issue.")
    if any(
        f.kind == "premium" and f.amount > 0 and f.date > case.stop_funding_date for f in case.flows
    ):
        raise ValueError("The selected stop-funding path contains later premiums.")
