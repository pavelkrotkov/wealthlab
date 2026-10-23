"""Reject ambiguous identifiers, unresolved provenance and unsupported references."""

from wealthlab.portfolio.chronology import validate_dates
from wealthlab.portfolio.fee_validation import validate_fees
from wealthlab.portfolio.harvest_validation import validate_harvest
from wealthlab.portfolio.policy_validation import validate_policies
from wealthlab.portfolio.tax_reporting import validate_tax_cases
from wealthlab.portfolio.terminal_exit import validate_exit


def validate(case):
    validate_fees(case)
    validate_exit(case)
    validate_harvest(case)
    validate_tax_cases(case)
    validate_policies(case)
    validate_wash_context(case)
    validate_dates(case)
    validate_ids(case)
    validate_references(case)


def validate_ids(case):
    groups = (case.accounts, case.securities, case.lots, case.trades)
    for group in groups:
        if len({item.id for item in group}) != len(group):
            raise ValueError(
                "Account, security, lot and trade IDs must be unique within each type."
            )
        if any(item.provenance == "unresolved" for item in group):
            raise ValueError(
                "Resolve critical account, security, lot and trade inputs before calculating."
            )


def validate_references(case):
    accounts = {item.id for item in case.accounts}
    securities = {item.id for item in case.securities}
    for item in [*case.lots, *case.trades]:
        if item.account_id not in accounts or item.security_id not in securities:
            raise ValueError("Every lot/trade must reference a configured account and security.")
    if set(case.closing_prices) != securities:
        raise ValueError("Provide an explicit closing price for every security.")


def validate_wash_context(case):
    """Either jurisdiction needs the same complete household purchase history.

    A per-security group cannot silently stand in for unsupported conversion ratios.
    """
    if not (case.federal_wash_tracking or case.nj_wash_treatment == "federal_rules"):
        return
    if not case.opening_wash_context_complete:
        raise ValueError(
            "Wash tracking requires complete opening household context: "
            "all retained purchases in the prior 30 days, adjusted bases, and no "
            "unresolved pre-opening loss sales. Extend the case earlier when needed."
        )
    groups = [security.wash_group for security in case.securities]
    if len(groups) != len(set(groups)):
        raise ValueError(
            "Cross-security substantially-identical matching requires conversion rules "
            "not yet supported. Use the same security ID across household accounts."
        )
