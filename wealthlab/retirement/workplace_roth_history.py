"""Source histories identify one ordinary contract, independently of a requested cash order.

A missing participation year is accepted only for an empty opening contract;
its first actual funded payroll deposit can establish the clock. Historical
cost may exceed current value after losses and is not clipped at validation.
"""


def validate_contract(contract, accounts, members, opening_year):
    confirmations = (
        contract.complete_vested_ordinary_designated_roth_contract_confirmed,
        contract.no_inplan_conversions_inherited_loans_nua_or_other_special_history_confirmed,
        contract.complete_cash_events_excluded_from_other_inputs_confirmed,
        contract.independent_nj_basis_and_conditional_treatment_confirmed,
    )
    if not all(confirmations):
        raise ValueError(
            "Confirm complete ordinary Roth history and independent conditional NJ cost."
        )
    owners = {accounts[s].owner for s in contract.sources}
    if len(owners) != 1:
        raise ValueError("A designated Roth contract has one owner across all its subaccounts.")
    born = members[next(iter(owners))].birth_date
    if contract.separation_date <= born:
        raise ValueError("Roth source separation must follow its owner's birth.")
    validate_clock(contract, accounts, born.year, opening_year)


def validate_clock(contract, accounts, birth_year, opening_year):
    first = contract.first_federal_contribution_year
    value = sum(accounts[s].balance for s in contract.sources)
    if first is None:
        if value or contract.federal_basis or contract.nj_basis:
            raise ValueError("Opening Roth value or cost needs its first participation year.")
    elif not birth_year <= first <= opening_year:
        raise ValueError("Opening Roth participation year must lie between birth and projection.")
