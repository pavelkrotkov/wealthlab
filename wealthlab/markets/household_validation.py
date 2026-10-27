"""Fail before projecting any path when the accounting profile is unsupported.

A complete binding is necessary to prevent unmapped securities from retaining
fixed prices while the result is presented as a household market simulation.
Positive cash yield needs an explicit assumed tax character. Reinventing an
issuer distribution history from total-return marks would lose real tax and
basis events, so that convention requires a separate adapter.
"""

from wealthlab.household.calendar import months
from wealthlab.markets.cash_scope import cash_only
from wealthlab.markets.collectible_scope import validate as validate_collectibles
from wealthlab.markets.drilling_compile import validate as validate_drilling
from wealthlab.markets.employer_validation import validate as validate_employers
from wealthlab.markets.exchange_compile import validate as validate_exchange
from wealthlab.markets.guardrails import validate as validate_guardrail
from wealthlab.markets.hsa_validation import validate as validate_hsa
from wealthlab.markets.medical_inflation import validate as validate_medical
from wealthlab.markets.option_validation import validate as validate_options
from wealthlab.markets.qoz_validation import validate as validate_qoz
from wealthlab.markets.sleeve_compile import validate as validate_sleeves
from wealthlab.markets.wrapper_compile import validate as validate_wrappers
from wealthlab.portfolio.household_validation import validate as validate_lots


def validate(scenario, batch, binding, index):
    if scenario.tax_plan is None:
        raise ValueError("Market execution requires explicit household tax.")
    if scenario.lot_plan is not None:
        validate_lots(scenario)
    validate_hsa(scenario, batch, binding)
    validate_wrappers(scenario, batch, binding)
    validate_employers(scenario, batch, binding)
    validate_sleeves(scenario, batch, binding)
    validate_exchange(scenario, batch, binding)
    validate_options(scenario, batch, binding)
    validate_drilling(scenario, batch, binding)
    validate_path(scenario, batch, index)
    validate_qoz(scenario, batch, binding, index)
    validate_bindings(scenario, batch, binding)
    validate_inflation(scenario, binding)
    validate_medical(scenario, binding)
    if binding.spending_guardrail is not None:
        validate_guardrail(scenario, binding.spending_guardrail)


def validate_path(scenario, batch, index):
    if not 0 <= index < len(batch.mark_returns):
        raise ValueError("Path index lies outside this realized market batch.")
    inputs = batch.metadata["input"]
    if (str(scenario.start), str(scenario.end)) != (inputs["start"], inputs["end"]):
        raise ValueError("Household and market horizons must match exactly.")
    validate_trading_scope(scenario, batch)


def validate_trading_scope(scenario, batch):
    if scenario.lot_plan and batch.metadata["return_convention"] != "price_plus_cash":
        raise ValueError("Taxable household paths require separate price returns and cash yields.")
    if scenario.lot_plan and scenario.lot_plan.case.trades:
        raise ValueError("Manual dated trades need a market execution-price adapter.")


def validate_bindings(scenario, batch, binding):
    confirm_scope(binding)
    identities = [b.security_id for b in binding.securities]
    actual = actual_securities(scenario)
    if not cash_only(scenario) and not any(
        (
            actual,
            binding.hsa_securities,
            binding.wrappers,
            binding.employers,
            binding.sleeves,
            binding.exchange_factors,
            binding.medical_bill_inflation,
            binding.options,
            binding.drilling,
            binding.qoz,
            scenario.property_plan,
        )
    ):
        raise ValueError(
            "Bind securities or supported wrappers, employer, property or medical cash profiles."
        )
    if len(identities) != len(set(identities)) or set(identities) != actual:
        raise ValueError("Bind every linked security exactly once.")
    if any(b.factor not in batch.assets for b in binding.securities):
        raise ValueError("Unknown market factor in household security binding.")
    validate_collectibles(scenario, batch, binding)


def validate_inflation(scenario, binding):
    ids = binding.inflation_expenses
    expenses = {e.id: e for e in scenario.expenses}
    if len(ids) != len(set(ids)) or not set(ids) <= expenses.keys():
        raise ValueError("Inflation expense IDs must be unique existing household expenses.")
    if any(expenses[i].annual_growth != 0 for i in ids):
        raise ValueError("Market-indexed expenses need zero separate annual growth.")


def validate_batch(scenario, batch):
    dates = tuple(start for start, _ in months(scenario.start, scenario.end))
    if batch.mark_returns.ndim != 3:
        raise ValueError("Market batch marks require path, month and factor axes.")
    expected = (batch.mark_returns.shape[0], len(dates), len(batch.assets))
    actual_shapes = (
        batch.mark_returns.shape,
        batch.cash_yields.shape,
        batch.inflation.shape,
        batch.locked.shape,
    )
    expected_shapes = (expected, expected, expected[:2], expected[1:])
    if tuple(batch.dates) != dates or actual_shapes != expected_shapes:
        raise ValueError("Market batch observation dates/shapes must cover every household month.")


def confirm_scope(binding):
    if not all(
        (
            binding.ordinary_cash_character_confirmed,
            binding.other_accounts_unmodeled_returns_confirmed,
        )
    ):
        raise ValueError("Confirm ordinary yield tax character and other-account return scope.")


def actual_securities(scenario):
    if scenario.lot_plan is None:
        return set()
    return {s.id for s in scenario.lot_plan.case.securities}
