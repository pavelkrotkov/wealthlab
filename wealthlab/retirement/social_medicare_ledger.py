"""Turn native entitlement records into gross tax recognition and net household receipts.

The existing claim validator runs before this ledger. Quotes arrive from the
current Medicare lookback, so a later tax result cannot change an earlier
claim or premium. Only actual withheld amounts credit a current bill.
"""

from collections import defaultdict
from decimal import Decimal

from wealthlab.retirement.social import run
from wealthlab.retirement.social_medicare_math import calculate
from wealthlab.tax.facts import FederalIncome
from wealthlab.tax.nj_facts import NJIncome
from wealthlab.tax.projection_inputs import TaxEvent


class Benefits:
    def __init__(self, scenario):
        self.rows = defaultdict(list)
        for row in run(scenario.social_security)["cash_months"]:
            self.rows[row["payment_month"]].append(row)
        self.own_insured = {p.id: p.own_insured for p in scenario.social_security.members}
        self.started = set()
        self.log = []

    def month(self, when, bills, book):
        current = {b["member"]: b for b in bills}
        events, payments = [], []
        for row in self.rows.get(when, ()):
            if not row["entitlement_before_offsets"]:
                continue
            member = row["member"]
            self.validate_start(member, when, book["rows"])
            active = "own_with_delayed_credits" if self.own_insured[member] else "spousal_excess"
            bill = current.get(member)
            result = calculate(row, bill, active)
            credit(book, bill, when, member, result)
            events.append(tax_event(when, member, result))
            payments.append(
                dict(
                    member=member,
                    entitlement_month=row["entitlement_month"],
                    payment_month=when,
                    **result,
                )
            )
        self.log.extend(payments)
        return events, summary(payments)

    def validate_start(self, member, when, bills):
        if member in self.started:
            return
        # ponytail: current-premium profile only; accumulated premium collection
        # needs component histories and the separate SSA arrears priority model.
        if any(b["member"] == member and b["date"] < when and b["unfunded"] for b in bills):
            raise ValueError(
                "Unpaid Medicare bills at benefit start require "
                "the premium-arrears collection layer."
            )
        self.started.add(member)


def credit(book, bill, when, member, result):
    amount = result["part_b_withheld"] + result["part_d_irmaa_withheld"]
    if bill is not None and amount:
        bill["paid"] += amount
        bill["unfunded"] -= amount
        book["payments"].append(
            dict(
                date=when,
                due=bill["id"],
                member=member,
                amount=amount,
                source="ssa_current_premiums",
            )
        )


def tax_event(when, member, result):
    return TaxEvent(
        date=when,
        description=f"SSA Medicare-adjusted {member}",
        cash_received=result["cash_received"],
        federal=FederalIncome(social_security=result["gross_credited"]),
        new_jersey=NJIncome(),
    )


def summary(payments):
    def total(key):
        return sum((r[key] for r in payments), Decimal(0))

    return dict(
        social_security_cash=total("cash_received"),
        social_security_gross_credited=total("gross_credited"),
        social_security_part_b_withheld=total("part_b_withheld"),
        social_security_part_d_irmaa_withheld=total("part_d_irmaa_withheld"),
        social_security_premium_rounding_change=total("change_from_no_premium_rounding"),
    )
