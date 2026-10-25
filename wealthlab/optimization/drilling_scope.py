"""A fingerprint detects changed search inputs; it certifies no legal or financial fact."""

import hashlib
import json


def fingerprint(search_scope):
    try:
        encoded = json.dumps(search_scope, sort_keys=True, separators=(",", ":"), allow_nan=False)
    except (TypeError, ValueError) as error:
        raise ValueError(
            "Pass the complete normalized JSON search scope, excluding its envelope."
        ) from error
    return hashlib.sha256(encoded.encode()).hexdigest()


def validate_envelope(household, envelope, search_scope):
    validate_confirmation(envelope)
    if envelope.as_of > household.start or envelope.valid_through < household.end:
        raise ValueError(
            "The drilling envelope must be known at opening and cover the full horizon."
        )
    if not isinstance(search_scope, dict) or search_scope.get("household") != household.model_dump(
        mode="json"
    ):
        raise ValueError("The complete drilling search scope must retain its original household.")
    if envelope.search_sha256 != fingerprint(search_scope):
        raise ValueError(
            "Changed drilling search inputs require a new independently sourced envelope."
        )


def validate_confirmation(envelope):
    if (
        envelope.provenance == "unresolved"
        or not envelope.source.strip()
        or not all(
            (
                envelope.all_candidate_employment_income_funding_and_bound_price_paths_confirmed,
                envelope.supplied_legal_se_qbi_amt_history_limits_recapture_release_facts_confirmed,
            )
        )
    ):
        raise ValueError(
            "Confirm independent drilling facts across ALL candidates and bound paths."
        )
    if envelope.full_tax_optimization_supported is not False:
        raise ValueError("Supplied drilling facts cannot establish full-tax optimization support.")


def validate_releases(plan, envelope):
    timings = [plan.federal_exit_loss_timing, plan.nj_exit_loss_timing]
    timings.extend(
        timing
        for row in plan.observations
        for item in row.deductions
        for timing in (item.federal_timing, item.nj_timing)
    )
    if any(t.release_on and t.release_on > envelope.valid_through for t in timings):
        raise ValueError(
            "The independent drilling envelope must cover every supplied release date."
        )
