"""Require a complete ordinary invested-HSA path mapping and replacement confirmation.

Total-return marks cannot silently become separate price and income events.
Actual manual trade prices require a different execution adapter. Existing lot
liquidity dates remain effective when generated scenario locks replace inputs.
"""

from wealthlab.retirement.hsa_household_validation import validate as validate_household


def validate(scenario, batch, binding):
    plan = scenario.hsa_plan
    investments = plan.investments if plan else None
    if investments is None:
        if binding.hsa_securities or binding.replace_hsa_observations_confirmed:
            raise ValueError("HSA market bindings require a household investment book.")
        return
    validate_household(scenario)
    validate_scope(investments, batch, binding)
    validate_bindings(investments, batch, binding)


def validate_bindings(investments, batch, binding):
    actual = {s.id for s in investments.case.securities}
    ids = [s.security_id for s in binding.hsa_securities]
    if len(ids) != len(set(ids)) or set(ids) != actual:
        raise ValueError("Bind every invested HSA security exactly once.")
    if any(s.factor not in batch.assets for s in binding.hsa_securities):
        raise ValueError("Unknown market factor in invested HSA bindings.")


def validate_scope(investments, batch, binding):
    if not binding.replace_hsa_observations_confirmed:
        raise ValueError("Confirm replacement of entered HSA prices, distributions and locks.")
    if investments.case.trades:
        raise ValueError("Manual HSA trades need a market execution-price adapter.")
    if batch.metadata["return_convention"] != "price_plus_cash":
        raise ValueError("Invested HSA paths require separate price returns and cash yield.")
