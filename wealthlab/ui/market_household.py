"""Edit and run household policies on a reproducible realized batch.

The optional synthetic guardrail demonstrates an observed-wealth spending
policy. Its cuts remain visible separately from unmet spending and taxes.
The paired alternative receives the same realized batch and selected indices;
changing a household policy never regenerates a different set of returns.
"""

import json

import streamlit as st

from wealthlab.household.scenario import Scenario
from wealthlab.markets.employer_example import synthetic as employer_example
from wealthlab.markets.guardrail_example import enable
from wealthlab.markets.household_example import synthetic
from wealthlab.markets.household_inputs import HouseholdBinding
from wealthlab.markets.household_run import paired, run
from wealthlab.markets.hsa_example import synthetic as hsa_example
from wealthlab.markets.hsa_payroll_example import synthetic as hsa_payroll_example
from wealthlab.markets.inputs import MarketCase
from wealthlab.markets.medical_example import synthetic as medical_example
from wealthlab.markets.option_example import synthetic as option_example
from wealthlab.markets.paths import generate
from wealthlab.markets.policy_example import CHOICES
from wealthlab.markets.policy_example import enable as policy_example
from wealthlab.markets.rebalance_example import synthetic as rebalance_example
from wealthlab.markets.rollover_example import synthetic as rollover_example
from wealthlab.markets.roth_cash_example import synthetic as roth_cash_example
from wealthlab.markets.sleeve_example import synthetic as sleeve_example
from wealthlab.markets.stresses import NAMES
from wealthlab.markets.workplace_example import synthetic as workplace_example
from wealthlab.markets.workplace_rmd_example import synthetic as workplace_rmd_example
from wealthlab.markets.wrapper_example import synthetic as wrapper_example
from wealthlab.ui import market_rebalance
from wealthlab.ui.market_household_results import display
from wealthlab.ui.market_hsa_payroll import controls as paired_controls
from wealthlab.ui.market_hsa_payroll import policy_text
from wealthlab.ui.market_option_results import selection as option_selection
from wealthlab.ui.sleeve_loss_assumptions import controls as loss_controls
from wealthlab.ui.uploads import invalid, source


def show():
    st.subheader("Actual household market funding")
    st.caption(
        "Realized paths fund spending through the same household tax/cash ledger. Selected budgets "
        "and medical bills use prior CPI; HSA election bounds remain explicit. Invested HSAs use "
        "actual lots, observed prices, cash yield and sale locks. Other accounts keep "
        "entered schedules. The two-year synthetic horizon does not cover retirement to age 100. "
        "Dated sales and harvesting use current marks. IRA/529 proxies and employer factors reuse "
        "their ledgers; employment responds next month. Sleeve taxes use supplied allocations. "
        "Discretionary cuts and constrained taxable-account rebalancing are reported separately."
    )
    mode = st.selectbox(
        "Household market mode", ["deterministic", "monte_carlo", "historical", "stress"]
    )
    stresses = (
        [*NAMES, "short_squeeze"]
        if st.session_state.get("market_account_scope") == "Long-short household"
        else NAMES
    )
    stress = st.selectbox("Household named stress", stresses, disabled=mode != "stress")
    household, market, binding = account_example(mode, stress)
    household = loss_controls(household)
    if st.checkbox("Use synthetic discretionary guardrail", key="market_guardrail_example"):
        household, binding = enable(household, binding)
    if household.lot_plan is not None and not household.lot_plan.rebalances:
        choice = st.selectbox("Synthetic lot policy", CHOICES, key="market_policy_example")
        household, binding = policy_example(household, binding, choice)
    default = json.dumps(
        dict(
            household=household.model_dump(mode="json"),
            market=market.model_dump(mode="json"),
            binding=binding.model_dump(mode="json"),
        ),
        indent=2,
    )
    uploaded = st.file_uploader("Load household market run JSON", type="json")
    if source(uploaded, default, "market_household") is None:
        return
    with st.form("market_household"):
        edited = st.text_area(
            "Household, market and explicit bindings (JSON)",
            key="market_household_editor",
            height=400,
        )
        count = st.number_input("Maximum paths to execute", min_value=1, max_value=5000, value=1)
        st.caption(
            "Full tax-ledger execution can take seconds per path; use a small run to check inputs."
        )
        alternative, match_hsa = paired_controls()
        market_rebalance.controls()
        submitted = st.form_submit_button("Project actual household paths", type="primary")
    if submitted:
        calculate(edited, count, alternative, match_hsa)
    if "market_household_result" in st.session_state:
        display(st.session_state["market_household_result"])


def calculate(edited, count, alternative, match_hsa=False):
    try:
        data = json.loads(edited or "")
        household = Scenario.model_validate(data["household"])
        case = MarketCase.model_validate(data["market"])
        binding = HouseholdBinding.model_validate(data["binding"])
        alternative = policy_text(household, alternative, match_hsa)
        alternative = market_rebalance.policy_text(household, alternative)
        batch = generate(case)
        indices = range(min(int(count), len(batch.mark_returns)))
        progress = st.progress(0)
        result = run(
            household,
            batch,
            binding,
            indices,
            progress=lambda done, total: progress.progress(done / total),
        )
        comparison = None
        if alternative.strip():
            other_household, other_binding = paired_inputs(alternative, binding)
            other = run(other_household, batch, other_binding, indices)
            comparison = dict(result=other, differences=paired(result, other))
        st.session_state.update(
            market_household_result=dict(
                baseline=result, comparison=comparison, batch=batch.export()
            ),
            market_household_input=edited,
        )
    except (ValueError, KeyError, TypeError) as error:
        invalid(error, "market_household")


def paired_inputs(text, binding):
    data = json.loads(text)
    if "household" in data:
        if set(data) - {"household", "binding"}:
            raise ValueError(
                "Paired policies accept household/binding only; the batch stays shared."
            )
        binding = HouseholdBinding.model_validate(data.get("binding", binding.model_dump()))
        data = data["household"]
    return Scenario.model_validate(data), binding


def account_example(mode, stress):
    scope = st.selectbox(
        "Synthetic account scope",
        [
            "Taxable lots",
            "Taxable rebalancing",
            "IRA and education proxies",
            "Employer and employment",
            "Employee 401(k)",
            "Workplace RMDs",
            "Direct plan rollovers",
            "Designated Roth plan cash",
            "Long-short household",
            "Options household",
            "Medical bill inflation",
            "Invested HSA",
            "HSA payroll and employment",
        ],
        key="market_account_scope",
    )
    if scope == "Options household":
        return option_example(mode, stress, option_selection())
    starter = {
        "Taxable lots": synthetic,
        "Taxable rebalancing": rebalance_example,
        "IRA and education proxies": wrapper_example,
        "Employer and employment": employer_example,
        "Employee 401(k)": workplace_example,
        "Workplace RMDs": workplace_rmd_example,
        "Direct plan rollovers": rollover_example,
        "Designated Roth plan cash": roth_cash_example,
        "Long-short household": sleeve_example,
        "Medical bill inflation": medical_example,
        "Invested HSA": hsa_example,
        "HSA payroll and employment": hsa_payroll_example,
    }[scope]
    return starter(mode, stress)
