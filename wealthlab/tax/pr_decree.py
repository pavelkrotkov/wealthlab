"""Current Act60 §§2022.01/.02: application cutover, dated grant and explicit eligibility."""

from datetime import date

from wealthlab.tax.pr_residence import MET


def qualification(decree, annual):
    reasons = []
    claims = claim_values(decree)
    if decree.status not in MET or any(claim not in MET for claim in claims):
        reasons.append(
            "Decree conditions are denied, unset or failed; ordinary alternative remains runnable."
        )
    reasons += date_reasons(decree)
    if annual.baseline.filing.status != "single":
        reasons.append("The incentive profile currently supports one single-filing adult only.")
    if decree.status == "confirmed" and not decree.evidence.strip():
        reasons.append("Confirmed decree claims need a supplied evidence reference.")
    if decree.legacy_transition_election:
        reasons.append("Legacy decree modification/election requires its actual amended terms.")
    return dict(
        eligible=not reasons, conditional="assumed" in [decree.status, *claims], reasons=reasons
    )


def rate(decree, received):
    if (
        received < max(decree.effective_from, decree.residence_since)
        or received > decree.valid_until
    ):
        return None
    # Act38-2026 keys the regime to application date. Grant/effective date
    # still limits actual receipts but does not move an applicant across regimes.
    legacy = decree.application_date <= date(2026, 12, 31)
    end = date(2036 if legacy else 2056, 1, 1)
    if received >= end:
        return None
    return 0 if legacy else 4


def pre_rate(decree, received, resident_since):
    anniversary = resident_since.replace(year=resident_since.year + 10)
    if received > anniversary and rate(decree, received) is not None:
        return 5
    return 15


def date_reasons(decree):
    reasons = []
    dates = [
        decree.granted_on,
        decree.application_date,
        decree.effective_from,
        decree.valid_until,
        decree.residence_since,
    ]
    if any(value is None for value in dates):
        reasons.append("Application, effectiveness, expiry and residence dates must be explicit.")
    elif not (
        decree.application_date <= decree.granted_on <= decree.valid_until
        and decree.effective_from <= decree.valid_until
    ):
        reasons.append("Decree dates are inconsistent.")
    return reasons


def claim_values(decree):
    claims = [
        decree.eligibility_history,
        decree.compliance,
        decree.not_revoked,
        decree.prior_residence_window_2006_2012,
    ]
    if decree.application_date and decree.application_date.year >= 2027:
        claims.append(decree.six_prior_years_nonresident)
    return claims
