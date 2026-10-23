"""Fee schedules identify every billing choice; missing prices never use future marks.

An assessment uses the ending snapshot for its stated accrual period. Contiguous
periods may share a boundary; overlapping or repeated assessments are rejected.
A supplied contractual base is explicit and does not imply owned portfolio capital.
"""


def validate_fees(case):
    accounts = {item.id for item in case.accounts}
    securities = {item.id for item in case.securities}
    ids = {item.id for item in [*case.trades, *case.sale_policies, *case.harvest_policies]}
    for schedule in case.fee_schedules:
        if schedule.id in ids or schedule.provenance == "unresolved":
            raise ValueError("Fee IDs must be distinct and fee assumptions resolved.")
        ids.add(schedule.id)
        validate_scope(schedule, accounts, securities)
        validate_periods(case, schedule, securities)


def validate_scope(schedule, accounts, securities):
    if schedule.payment_account not in accounts or not set(schedule.account_ids) <= accounts:
        raise ValueError("Fee payment and valuation accounts must be configured.")
    if not set(schedule.security_ids) <= securities:
        raise ValueError("Fee valuation securities must be configured.")
    for keys in (schedule.account_ids, schedule.security_ids):
        if len(keys) != len(set(keys)):
            raise ValueError("Fee scope must not contain duplicate IDs.")


def validate_periods(case, schedule, securities):
    previous = None
    for period in schedule.periods:
        if not case.as_of <= period.start <= period.date <= case.end:
            raise ValueError("Fee accrual and assessment dates must lie inside the case.")
        if previous is not None and (period.start < previous or period.date <= previous):
            raise ValueError("Fee periods must be chronological and cannot overlap.")
        if set(period.prices) != securities:
            raise ValueError("Every fee assessment requires its own complete price snapshot.")
        previous = period.date
