"""Fail before projecting any path when the accounting profile is unsupported.

A complete binding is necessary to prevent unmapped securities from retaining
fixed prices while the result is presented as a household market simulation.
Positive cash yield needs an explicit assumed tax character. Reinventing an
issuer distribution history from total-return marks would lose real tax and
basis events, so that convention requires a separate adapter.
"""

from wealthlab.portfolio.household_validation import validate as validate_lots


def validate(scenario, batch, binding, index):
    if scenario.lot_plan is None or scenario.tax_plan is None:
        raise ValueError("Market execution requires actual linked taxable lots and household tax.")
    validate_lots(scenario)
    validate_path(scenario, batch, index)
    validate_bindings(scenario, batch, binding)
    validate_inflation(scenario, binding)


def validate_path(scenario, batch, index):
    if not 0 <= index < len(batch.mark_returns):
        raise ValueError("Path index lies outside this realized market batch.")
    inputs = batch.metadata["input"]
    if (str(scenario.start), str(scenario.end)) != (inputs["start"], inputs["end"]):
        raise ValueError("Household and market horizons must match exactly.")
    validate_trading_scope(scenario, batch)


def validate_trading_scope(scenario, batch):
    if batch.metadata["return_convention"] != "price_plus_cash":
        raise ValueError("Taxable household paths require separate price returns and cash yields.")
    if scenario.lot_plan.case.trades:
        raise ValueError("Manual dated trades need a market execution-price adapter.")


def validate_bindings(scenario, batch, binding):
    if not all(
        (
            binding.ordinary_cash_character_confirmed,
            binding.other_accounts_unmodeled_returns_confirmed,
        )
    ):
        raise ValueError("Confirm ordinary yield tax character and other-account return scope.")
    identities = [b.security_id for b in binding.securities]
    actual = {s.id for s in scenario.lot_plan.case.securities}
    if len(identities) != len(set(identities)) or set(identities) != actual:
        raise ValueError("Bind every linked security exactly once.")
    if any(b.factor not in batch.assets for b in binding.securities):
        raise ValueError("Unknown market factor in household security binding.")


def validate_inflation(scenario, binding):
    ids = binding.inflation_expenses
    expenses = {e.id: e for e in scenario.expenses}
    if len(ids) != len(set(ids)) or not set(ids) <= expenses.keys():
        raise ValueError("Inflation expense IDs must be unique existing household expenses.")
    if any(expenses[i].annual_growth != 0 for i in ids):
        raise ValueError("Market-indexed expenses need zero separate annual growth.")
