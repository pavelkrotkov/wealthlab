"""Gross invested-HSA positions and unsettled obligations must close before exit ranking."""

from decimal import Decimal


def lots_closed(lots):
    return all(Decimal(lot["quantity"]) == 0 for lot in lots)


def hsa_closed(household, row):
    if household.hsa_plan is None or household.hsa_plan.investments is None:
        return True
    audit = row.get("hsa_audit", {}).get("investments")
    if audit is None:
        return False
    return lots_closed(audit["lots"]) and all(
        Decimal(value) == 0
        for name in ("cash_by_account", "distribution_receivable", "fee_owed_by_account")
        for value in audit[name].values()
    )
