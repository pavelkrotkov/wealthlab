"""Composable synthetic menus keep imported household contracts outside starter generation.

Fixed existing option positions and new cash purchases are mutually exclusive
starter modes because the native engine owns one option book. Complete private
scenarios continue through the separate JSON import/editor without modification.
"""

import streamlit as st

from wealthlab.optimization.account_example import extend as with_accounts
from wealthlab.optimization.advisory_example import extend as with_advisory
from wealthlab.optimization.allocation_example import extend as with_allocations
from wealthlab.optimization.collectible_example import synthetic as collectible_starter
from wealthlab.optimization.contract_example import extend as with_contracts
from wealthlab.optimization.country_example import synthetic as country_starter
from wealthlab.optimization.diversification_example import extend as with_diversification
from wealthlab.optimization.drilling_example import confirm_synthetic
from wealthlab.optimization.drilling_example import extend as with_drilling
from wealthlab.optimization.employment_example import synthetic as employment_starter
from wealthlab.optimization.example import synthetic
from wealthlab.optimization.exchange_example import extend as with_exchange_choices
from wealthlab.optimization.life_example import extend as with_life_paths
from wealthlab.optimization.new_life_example import extend as with_new_life
from wealthlab.optimization.option_allocation_example import extend as with_new_options
from wealthlab.optimization.product_example import extend as with_products
from wealthlab.optimization.qoz_example import extend as with_qoz
from wealthlab.optimization.robustness_example import synthetic as robust
from wealthlab.ui.optimization_horizon import show as horizon_starter


def show():
    example = st.selectbox(
        "Synthetic starter",
        [
            "Short composable examples",
            "Full age-100 cash and stock example",
            "Gold treated as collectible sale timing",
            "Source-matched retirement and employer vesting",
            "Fixed PR country tax and retirement wages",
        ],
    )
    starter = preset(example)
    if starter is not None:
        return starter
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
    return advisory(purchases(starter))


def preset(example):
    if example == "Fixed PR country tax and retirement wages":
        st.caption(
            "Fixed synthetic PR residence and US-source wages; retirement changes actual "
            "dated wages and both native country tax bills. No relocation or eligibility "
            "choice. Default age-100 safety remains unproved by this short example."
        )
        return country_starter()
    if example == "Full age-100 cash and stock example":
        return horizon_starter()
    if example == "Gold treated as collectible sale timing":
        st.caption(
            "Original synthetic physical-gold classification, not a gold-fund tax ruling. "
            "Both sale dates share existing lots, separate federal/NJ bases and zero cash yield. "
            "Entered W-2 wages continue unchanged; this short example "
            "does not prove age-100 safety."
        )
        return collectible_starter()
    if example == "Source-matched retirement and employer vesting":
        st.caption(
            "Complete hypothetical work and employer-award profiles are paired with exact "
            "retirement dates. Early forfeiture and later vesting are supplied assumptions, "
            "not consequences inferred from account ownership. Edit or lock the choices below."
        )
        return employment_starter()


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
    if st.checkbox("Add synthetic QOZ subscription choices", key="qoz_starter"):
        starter = with_qoz(starter)
    if st.checkbox(
        "Add synthetic conditional drilling participation choices", key="drilling_starter"
    ):
        starter = with_drilling(starter)
    return starter


def advisory(starter):
    if st.checkbox("Add common sourced advisory AUM fees", key="optimizer_advisory_starter"):
        generated = with_advisory(starter)
        # This composer starts only from original synthetic factories. Finish its
        # complete illustrative scope after all builders; imported files never enter here.
        if generated.drilling_offers:
            return confirm_synthetic(generated.model_dump(mode="json"))
        return generated
    return starter
