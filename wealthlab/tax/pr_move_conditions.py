"""Move-year exceptions need history and prospective facts, not just arrival dates."""

from datetime import date


def move_conditions(residence, year, claims, reasons):
    status = residence.federal_bfr
    if status in {"full_year", "move_in"} and residence.presence_days < 183:
        reasons.append("This profile implements the 183-day presence route only.")
    if status == "move_in":
        claims += [residence.prior_three_nonresident, residence.next_three_resident]
        if not residence.local_start or residence.local_start > date(year, 7, 2):
            reasons.append("Move-in exception needs the last 183 days of qualifying tax home.")
    if status == "move_out":
        claims.append(residence.prior_two_resident)
        if not residence.local_end:
            reasons.append("Departure exception needs an explicit residence end.")
    return claims, reasons
