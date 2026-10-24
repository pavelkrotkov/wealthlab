"""A household sleeve owns its entire classified account and cannot be spent by another book.

The standalone outside-cash reserve is zero here: actual household receipts
supply collateral and settle debt. Complete tax/exit inputs are explicit
assumptions, rather than tax classifications inferred from an economic path.
"""

from wealthlab.products.long_short_validation import validate_terms


def validate_account(sleeve, accounts, forbidden):
    account = accounts.get(sleeve.account_id)
    validate_type(account)
    validate_terms(sleeve.case, {sleeve.case.long_factor, sleeve.case.short_factor})
    if account.id in forbidden:
        raise ValueError(
            "A sleeve cannot share another book, generic transfer or taxable funding source."
        )
    if sleeve.case.opening_equity != account.balance or sleeve.case.outside_cash != 0:
        raise ValueError("Reconcile sleeve opening equity and use zero separate outside cash.")
    if not sleeve.all_tax_recognition_and_exit_assumptions_supplied_confirmed:
        raise ValueError("Confirm complete supplied sleeve tax and exit assumptions.")


def validate_type(account):
    if (
        account is None
        or account.wrapper != "taxable"
        or account.currency != "USD"
        or account.monthly_fee
    ):
        raise ValueError("Sleeves need known USD taxable accounts with no generic account fees.")


def excluded_accounts(scenario):
    lots = {a.id for a in scenario.lot_plan.case.accounts} if scenario.lot_plan else set()
    funded = {s.account_id for s in scenario.tax_plan.funding_sources}
    transfers = {c.destination for c in scenario.contributions}
    return lots | funded | transfers
