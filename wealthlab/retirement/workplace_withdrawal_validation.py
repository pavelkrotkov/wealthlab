"""Fail closed for unsupported workplace basis, RMD years and special distributions.

This ordinary cash profile consumes already vested balances. Future-year basis,
RMDs, designated Roth distributions and direct rollovers have distinct rules;
none can masquerade as an ordinary eligible zero-basis cash withdrawal.
"""

from types import SimpleNamespace

from wealthlab.retirement.rmd import start_age


def validate(scenario):
    plan = scenario.workplace_plan
    cash = plan.cash_withdrawals
    if cash is None:
        return
    accounts = {a.id: a for a in scenario.accounts}
    members = {m.id: m for m in scenario.members}
    for source, profile in cash.profiles.items():
        if plan.products.get(source) != "pretax_401k":
            raise ValueError("Ordinary workplace cash requires a known pretax 401(k) source.")
        validate_profile(profile, members[accounts[source].owner].birth_date, scenario.end.year - 1)
    validate_orders(cash, plan, scenario)
    validate_separated_elections(cash, plan)


def validate_profile(profile, born, final_year):
    confirmations = (
        profile.eligible_nonperiodic_cash_distributions_confirmed,
        profile.fully_vested_zero_federal_and_nj_basis_confirmed,
        profile.no_inherited_loans_nua_hardship_or_other_special_features_confirmed,
        profile.complete_distributions_excluded_from_other_inputs_confirmed,
    )
    if not all(confirmations):
        raise ValueError("Confirm eligible workplace cash, vested zero basis and complete inputs.")
    if profile.separation_date <= born:
        raise ValueError("Workplace separation must follow the owner's birth date.")
    # Both conditional 1959 start ages are beyond a projection ending before age 73.
    if born.year == 1959 and final_year - born.year < 73:
        return
    owner = SimpleNamespace(birth_date=born, birth_1959_start_age=profile.birth_1959_start_age)
    if final_year - born.year >= start_age(owner):
        raise ValueError("Workplace RMD years require an account-specific RMD profile.")


def validate_orders(cash, plan, scenario):
    records = [*cash.orders, *plan.orders, *plan.returns, *plan.liquidity_locks]
    identities = [r.id for r in records]
    if len(identities) != len(set(identities)):
        raise ValueError("Workplace withdrawal/election/return/lock IDs must be unique.")
    for order in cash.orders:
        validate_order(order, cash.profiles, scenario)


def validate_order(order, profiles, scenario):
    if order.source not in profiles or order.provenance == "unresolved":
        raise ValueError("Workplace cash orders require resolved source profiles.")
    if not scenario.start <= order.date < scenario.end or order.date.day != 1:
        raise ValueError("Workplace cash withdrawals require in-horizon first-day dates.")
    if order.date < profiles[order.source].separation_date:
        raise ValueError("Ordinary workplace cash cannot precede confirmed separation.")


def validate_separated_elections(cash, plan):
    for order in plan.orders:
        profile = cash.profiles.get(order.destination)
        if profile is not None and order.date >= profile.separation_date:
            raise ValueError("New employee deferrals cannot fund the separated source plan.")
