"""Own-record US earned-wage scope prevents unsupported auxiliaries or opening debt disappearing."""


def validate(case):
    policy = case.work
    confirmations = (
        policy.complete_current_us_w2_wages_without_special_payments_confirmed,
        policy.no_prior_unmodeled_work_positions_or_reduction_credits_confirmed,
        policy.no_auxiliary_work_effects_in_this_profile_confirmed,
        policy.administrative_payment_timing_and_recovery_are_conditional_confirmed,
        policy.no_special_lump_sum_tax_election_assumed,
    )
    if not all(confirmations):
        raise ValueError(
            "Confirm earned-wage history, own-record scope and conditional cash timing."
        )
    people = {p.id for p in case.claims.members}
    validate_coverage(case, people)
    if set(policy.grace_used_before_projection) != people:
        raise ValueError("Declare prior grace-year usage separately for every member.")
    validate_records(policy)
    if any(p.death_date is not None or p.survivor_claim_month for p in case.claims.members):
        raise ValueError("This own-record work profile excludes dated death/survivor effects.")


def validate_coverage(case, people):
    policy = case.work
    if any(p.claim_month.year < case.claims.start_year for p in case.claims.members):
        raise ValueError(
            "Start the projection before benefits start; prior claims need opening work history."
        )
    expected = {(y, p) for y in range(case.claims.start_year, case.claims.end_year) for p in people}
    actual = {(row.year, row.member) for row in policy.years}
    if actual != expected or len(actual) != len(policy.years):
        raise ValueError("Provide one complete work report per calendar year and claim member.")


def validate_records(policy):
    ids = [row.id for row in policy.years]
    if len(ids) != len(set(ids)):
        raise ValueError("Work report IDs must be unique.")
    if any(row.provenance == "unresolved" for row in policy.years):
        raise ValueError("Resolve work report assumptions before projecting benefits.")
    if any(row.actual_monthly_wages is None for row in policy.years):
        raise ValueError("A standalone work case needs explicit realized monthly earned wages.")
