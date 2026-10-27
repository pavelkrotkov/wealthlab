"""Bounded 183-day route and explicit move-year conditions from IRS Pub 570."""

from datetime import date

from wealthlab.tax.pr_move_conditions import move_conditions
from wealthlab.tax.pr_residence_facts import Residence

MET = {"confirmed", "assumed"}


def federal_status(residence: Residence, year: int) -> dict:
    status = residence.federal_bfr
    if status == "no":
        return dict(eligible=False, conditional=residence.us_citizen == "assumed", reasons=[])
    claims = [residence.us_citizen, residence.tax_home, residence.closer_connection]
    reasons = []
    claims, reasons = move_conditions(residence, year, claims, reasons)
    if status == "unset" or any(claim not in MET for claim in claims):
        reasons.append("Bona fide residence/citizenship conditions are unconfirmed or failed.")
    return dict(
        eligible=None if reasons else True, conditional="assumed" in claims, reasons=reasons
    )


def local_period(residence: Residence, year: int) -> tuple[date, date] | None:
    if residence.local_start is None or residence.local_end is None:
        return None
    return max(date(year, 1, 1), residence.local_start), min(
        date(year, 12, 31), residence.local_end
    )


def excluded(row, residence, status, year):
    if not status["eligible"] or row.federal_source != "PR" or row.us_government_wages:
        return False
    if residence.federal_bfr == "move_out":
        return row.received <= residence.local_end
    return True
