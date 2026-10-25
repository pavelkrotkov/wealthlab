"""Composable synthetic menus keep imported household contracts outside starter generation.

Fixed existing option positions and new cash purchases are mutually exclusive
starter modes because the native engine owns one option book. Complete private
scenarios continue through the separate JSON import/editor without modification.
"""

import streamlit as st

from wealthlab.optimization.account_example import extend as with_accounts
from wealthlab.optimization.allocation_example import extend as with_allocations
from wealthlab.optimization.contract_example import extend as with_contracts
from wealthlab.optimization.diversification_example import extend as with_diversification
from wealthlab.optimization.drilling_example import extend as with_drilling
from wealthlab.optimization.example import synthetic
from wealthlab.optimization.exchange_example import extend as with_exchange_choices
from wealthlab.optimization.life_example import extend as with_life_paths
from wealthlab.optimization.new_life_example import extend as with_new_life
from wealthlab.optimization.option_allocation_example import extend as with_new_options
from wealthlab.optimization.product_example import extend as with_products
from wealthlab.optimization.robustness_example import synthetic as robust
from wealthlab.ui.optimization_horizon import show as horizon_starter


def show():
    example = st.selectbox(
        "Synthetic starter", ["Short composable examples", "Full age-100 cash and stock example"]
    )
    if example == "Full age-100 cash and stock example":
        return horizon_starter()
    checks = st.checkbox("Add synthetic deterministic, historical and stress checks")
    starter = robust() if checks else synthetic()
    for label, extend in (
        ("Add synthetic workplace, HSA and 529 policies", with_accounts),
        ("Add synthetic stock/bond diversification policies", with_diversification),
        ("Add synthetic conditional products with actual exits", with_products),
        ("Add synthetic cash-funded sleeve allocation choices", with_allocations),
        ("Add synthetic complete life-policy funding paths", with_life_paths),
        ("Add synthetic options and employer contract exits", with_contracts),
    ):
        if st.checkbox(label, key=label):
            starter = extend(starter)
    return purchases(starter)


def purchases(starter):
    new_options = st.checkbox(
        "Add synthetic cash-funded option allocation choices",
        disabled=starter.household.option_plan is not None,
        key="new_option_allocation_starter",
    )
    if new_options and starter.household.option_plan is None:
        starter = with_new_options(starter)
    if st.checkbox("Add synthetic exchange-fund contribution choices", key="exchange_path_starter"):
        starter = with_exchange_choices(starter)
    if st.checkbox("Add synthetic new life-policy purchase choices", key="new_life_starter"):
        starter = with_new_life(starter)
    if st.checkbox(
        "Add synthetic conditional drilling participation choices", key="drilling_starter"
    ):
        starter = with_drilling(starter)
    return starter
