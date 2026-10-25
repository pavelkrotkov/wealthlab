"""Insurance accounts contain net surrender equity and belong to one named member.

Generic transfers and fees bypass the policy basis ledger, so they are forbidden.
The opening account is already net of policy debt; the household must not subtract
that same debt again. Death protection remains a separate owner-level measure.
"""

from wealthlab.products.life_household_records import validate_values


def validate_account(scenario, holding, members):
    accounts = {a.id: a for a in scenario.accounts}
    account = accounts.get(holding.account_id)
    if account is None or account.wrapper != "insurance" or account.currency != "USD":
        raise ValueError("A life policy requires its own USD insurance account.")
    validate_funding(scenario, account, holding)
    if account.owner not in members:
        raise ValueError("A policy requires one specific member owner, not joint ownership.")
    if account.owner not in scenario.life_plan.insurance_need_by_owner:
        raise ValueError("Supply an independent insurance need for each policy owner.")
    if holding.contract.owner_birth_date != members[account.owner].birth_date:
        raise ValueError("Policy owner birth date must match the household member.")


def validate_funding(scenario, account, holding):
    if account.monthly_fee or any(c.destination == account.id for c in scenario.contributions):
        raise ValueError(
            "Policy fees and funding must use the policy ledger, not generic transfers."
        )
    validate_values(holding.opening_values)
    expected = holding.opening_values.gross_surrender_value - holding.contract.opening_loan
    if expected < 0 or account.balance != expected:
        raise ValueError("Policy opening account must equal gross surrender value less loan debt.")
