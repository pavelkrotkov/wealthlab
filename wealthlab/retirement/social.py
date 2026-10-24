"""Monthly ordinary retirement/spouse benefits with distinct entitlement and cash months."""

from datetime import date
from decimal import Decimal

from wealthlab.household.calendar import months
from wealthlab.retirement.social_amounts import dime, dollar, own_amount, pia, reduced
from wealthlab.retirement.social_dates import alive, distance, full_retirement_month, shift
from wealthlab.retirement.social_owl import compare
from wealthlab.retirement.social_survivor import amount as survivor_amount


def run(case):
    members = {person.id: person for person in case.members}
    fras = {person.id: full_retirement_month(person.birth_date) for person in case.members}
    rows = []
    # Include prior December entitlement for January cash; exclude final December
    # from issued cash until the following month. No host-year defaults are used.
    start, end = date(case.start_year - 1, 12, 1), date(case.end_year, 1, 1)
    for month, _ in months(start, end):
        for person in case.members:
            rows.append(benefit(case, person, month, members, fras))
    cash_rows = [
        row for row in rows if case.start_year <= row["payment_month"].year < case.end_year
    ]
    annual_cash = annual(cash_rows)
    return dict(
        monthly_entitlements=rows,
        cash_months=cash_rows,
        fra_months=fras,
        total_issued_before_offsets=sum(
            (r["issued_before_offsets"] for r in cash_rows), Decimal(0)
        ),
        annual_cash=annual_cash,
        owl_comparison=compare(case, annual_cash),
        mortality_assumptions=mortality_assumptions(case),
        claim_rule_policy=case.claim_rule_policy,
        future_cola_assumption=case.future_cola_assumption,
        sources=[
            "https://www.ssa.gov/OP_Home/cfr20/404/404-0410.htm",
            "https://www.ssa.gov/OP_Home/cfr20/404/404-0313.htm",
            "https://secure.ssa.gov/poms.nsf/links/0300615694",
            "https://secure.ssa.gov/poms.nsf/lnx/0300615320",
            "https://secure.ssa.gov/poms.nsf/lnx/0300615706",
        ],
    )


def benefit(case, person, month, members, fras):
    own_pia = pia(person, month, case.future_cola_assumption)
    own_base, own = own_amount(person, fras[person.id], month, own_pia)
    spouse = spouse_amount(case, person, month, members, fras, own_pia, own_base, own)
    survivor = survivor_amount(case, person, month, members, fras, own)
    entitlement = own + spouse + survivor["survivor_excess"]
    return dict(
        member=person.id,
        entitlement_month=month,
        payment_month=shift(month, 1),
        pia=own_pia,
        own_before_delayed_credits=own_base,
        own_with_delayed_credits=own,
        spousal_excess=spouse,
        **survivor,
        entitlement_before_offsets=entitlement,
        issued_before_offsets=dollar(entitlement),
    )


def spouse_amount(case, person, month, members, fras, own_pia, own_base, own):
    if not person.spousal_eligibility_confirmed:
        return Decimal(0)
    partner = members[person.partner]
    start = max(person.claim_month, partner.claim_month)
    if month < start or not alive(person, month) or not alive(partner, month):
        return Decimal(0)
    partner_pia = pia(partner, month, case.future_cola_assumption)
    original = dime(partner_pia / 2)
    excess = max(Decimal(0), original - own_pia)
    months_early = max(0, distance(start, fras[person.id]))
    combined_without_drc = own_base + reduced(excess, months_early, spouse=True)
    return max(Decimal(0), combined_without_drc - own)


def annual(rows):
    totals = {}
    for row in rows:
        key = row["payment_month"].year, row["member"]
        totals[key] = totals.get(key, Decimal(0)) + row["issued_before_offsets"]
    return [
        dict(year=year, member=member, issued_before_offsets=amount)
        for (year, member), amount in totals.items()
    ]


def mortality_assumptions(case):
    return dict(
        policy=case.survival_policy,
        members=[
            dict(
                id=p.id,
                death_date=p.death_date,
                survivor_claim_month=p.survivor_claim_month,
                survivor_eligibility_confirmed=p.survivor_eligibility_confirmed,
                survivor_pia_january_2026=p.survivor_pia_january_2026,
            )
            for p in case.members
        ],
    )
