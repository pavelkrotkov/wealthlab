"""Owl remains a limited reference, never an authority that overrides SSA-backed arithmetic.

A dated-death case requires exact entitlement and cash timing, whereas Owl's
annual stream uses a full-death-year convention. Exclude that scope explicitly
rather than forcing incompatible mortality inputs into the ordinary reference.
"""

import numpy as np

from wealthlab.retirement.social_dates import distance, seventieth_month


def compare(case, annual):
    reason = exclusion(case)
    if reason:
        return dict(status="outside_reference_scope", reason=reason, rows=[])
    from owlplanner.socialsecurity import compute_social_security_benefits

    count = case.end_year - case.start_year
    values, _ = compute_social_security_benefits(
        **arguments(case),
        horizons=np.full(len(case.members), count),
        N_i=len(case.members),
        N_n=count,
        thisyear=case.start_year,
    )
    native = {(r["year"], r["member"]): r["issued_before_offsets"] for r in annual}
    rows = [
        dict(
            year=case.start_year + n,
            member=person.id,
            native_issued=native[case.start_year + n, person.id],
            owl_reference=round(float(values[i, n]), 2),
            difference=round(
                float(native[case.start_year + n, person.id]) - float(values[i, n]), 2
            ),
        )
        for n in range(count)
        for i, person in enumerate(case.members)
    ]
    return dict(
        status="reference_only",
        rows=rows,
        limitations="Owl combined spousal DRC, pre-70 claim-year credits, "
        "rounding and plan-year fractions can differ; "
        "fractional PIA, COLA, deductions and offsets are outside this reference.",
    )


def exclusion(case):
    if has_mortality(case):
        return "Dated-death and survivor histories are outside this limited Owl reference."
    if unsupported_claim(case):
        return (
            "Owl reference excludes after-70 claims and PIA beyond its signed-32-bit input range."
        )
    if incompatible_pia(case):
        return "Owl's reference needs zero COLA and whole-dollar PIA; do not truncate supplied PIA."
    if len(case.members) == 2 and not all(p.spousal_eligibility_confirmed for p in case.members):
        return "Owl's two-person stream assumes both partner relationships; eligibility differs."
    return None


def arguments(case):
    return dict(
        pias=np.array([int(p.pia_january_2026) for p in case.members]),
        ages=np.array([distance(p.birth_date, p.claim_month) / 12 for p in case.members]),
        yobs=np.array([p.birth_date.year for p in case.members]),
        mobs=np.array([p.birth_date.month for p in case.members]),
        tobs=np.array([p.birth_date.day for p in case.members]),
    )


def unsupported_claim(case):
    return any(
        p.claim_month > seventieth_month(p.birth_date) or p.pia_january_2026 >= 2**31
        for p in case.members
    )


def has_mortality(case):
    return any(p.death_date is not None or p.survivor_claim_month is not None for p in case.members)


def incompatible_pia(case):
    return case.future_cola_assumption or any(p.pia_january_2026 % 1 for p in case.members)
