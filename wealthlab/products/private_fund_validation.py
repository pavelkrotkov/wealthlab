"""Fail closed outside the bounded, explicitly assumed cash-distribution fund profile.

The existing sleeve validator retains account ownership, tax-field and complete
monthly observation checks. These guards add the independent sponsor contract
and supplied-basis boundaries without changing ordinary margin accounts.
"""


def validate(sleeve, scenario):
    contract = sleeve.private_fund_contract
    if contract is None:
        return
    confirmed = (
        contract.eligibility_assumed_confirmed,
        contract.limited_liability_no_calls_assumed_confirmed,
        contract.cash_only_no_hot_assets_no_liability_changes_assumed_confirmed,
        contract.tax_basis_schedule_complete_assumed_confirmed,
    )
    if not all(confirmed):
        raise ValueError(
            "Confirm eligibility, liability, cash-only tax profile and basis schedule."
        )
    if sleeve.case.redemptions or sleeve.case.exit_at_horizon:
        raise ValueError("Fund exits must use contract requests, including terminal requests.")
    if sleeve.case.margin_policy != "liquidate_on_breach":
        raise ValueError("Private-fund margin is internal; investor cash calls are unsupported.")
    validate_records(contract)
    validate_dates(contract, scenario)


def validate_records(contract):
    records = [contract, *contract.requests, *contract.basis_adjustments]
    if any(r.provenance == "unresolved" for r in records):
        raise ValueError("Resolve private-fund contract, request and basis assumptions.")
    ids = [r.id for r in records]
    if len(ids) != len(set(ids)):
        raise ValueError("Private-fund contract record IDs must be unique.")


def validate_dates(contract, scenario):
    if (
        contract.federal_holding_start is not None
        and contract.federal_holding_start > scenario.start
    ):
        raise ValueError("An opening fund interest cannot have a future holding start.")
    if any(not scenario.start <= r.notice_date < scenario.end for r in contract.requests):
        raise ValueError("Fund notices must be inside the projection.")
    if any(not scenario.start <= r.date < scenario.end for r in contract.basis_adjustments):
        raise ValueError("Fund basis adjustments must be inside the projection.")
    if contract.basis_adjustments != sorted(contract.basis_adjustments, key=lambda r: r.date):
        raise ValueError("Fund basis adjustments must be chronological.")
