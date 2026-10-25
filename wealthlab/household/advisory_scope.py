"""Coverage is contractual: absence and unavailable valuation stages remain explicit.

A selected net account value is not a reconstructed gross position. Insurance
uses its native supplied net values. Wrapper marks applied only in later hooks
cannot be billed as if already observed at this earlier assessment snapshot.
"""


def validate_coverage(scenario, schedule):
    accounts = {a.id: a for a in scenario.accounts}
    ids = [c.account_id for c in schedule.covered]
    if len(ids) != len(set(ids)):
        raise ValueError("Advisory coverage cannot repeat an account within one schedule.")
    for covered in schedule.covered:
        validate_covered(covered, accounts)


def validate_covered(covered, accounts):
    if covered.presence == "if_present" and not covered.absence_permitted_by_source_confirmed:
        raise ValueError("Conditional advisory coverage needs source-confirmed absence terms.")
    account = accounts.get(covered.account_id)
    if account is None:
        if covered.presence == "required":
            raise ValueError("Required advisory valuation account is missing.")
        return
    validate_basis(account, covered)


def validate_basis(account, covered):
    if covered.value_basis.startswith("life_"):
        if account.wrapper != "insurance":
            raise ValueError("A life advisory basis requires a native insurance account.")
    elif account.wrapper in {"insurance", "property", "hsa", "education"}:
        raise ValueError(
            "This advisory stage lacks the selected net basis; use sourced life values or "
            "a supported current account-equity basis."
        )
