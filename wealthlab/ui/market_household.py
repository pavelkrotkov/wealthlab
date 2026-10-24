"""Edit and run household policies on a reproducible realized batch.

The optional synthetic guardrail demonstrates an observed-wealth spending
policy. Its cuts remain visible separately from unmet spending and taxes.
The paired alternative receives the same realized batch and selected indices;
changing a household policy never regenerates a different set of returns.
"""

import json

import streamlit as st

from wealthlab.household.scenario import Scenario
from wealthlab.markets.guardrail_example import enable
from wealthlab.markets.household_example import synthetic
from wealthlab.markets.household_inputs import HouseholdBinding
from wealthlab.markets.household_run import paired, run
from wealthlab.markets.inputs import MarketCase
from wealthlab.markets.paths import generate
from wealthlab.markets.stresses import NAMES
from wealthlab.ui.market_household_results import display
from wealthlab.ui.uploads import invalid, source


def show():
    st.subheader("Actual household market funding")
    st.caption(
        "Month-end prices fund spending through actual taxable lots and the same tax return. "
        "Opening holdings receive separately taxed cash yield; selected expenses use prior "
        "realized CPI. Other accounts retain their explicit entered schedules. The synthetic "
        "two-year horizon does not cover retirement through age 100. Automatic rebalancing, "
        "harvesting and employer-factor binding remain unfinished. "
        "Optional discretionary guardrails use observed real wealth; "
        "their cuts are reported separately."
    )
    mode = st.selectbox(
        "Household market mode", ["deterministic", "monte_carlo", "historical", "stress"]
    )
    stress = st.selectbox("Household named stress", NAMES)
    household, market, binding = synthetic(mode, stress)
    if st.checkbox("Use synthetic discretionary guardrail", key="market_guardrail_example"):
        household, binding = enable(household, binding)
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
        alternative = st.text_area("Optional paired household policy (JSON)", value="", height=120)
        submitted = st.form_submit_button("Project actual household paths", type="primary")
    if submitted:
        calculate(edited, count, alternative)
    if "market_household_result" in st.session_state:
        display(st.session_state["market_household_result"])


def calculate(edited, count, alternative):
    try:
        data = json.loads(edited or "")
        household = Scenario.model_validate(data["household"])
        case = MarketCase.model_validate(data["market"])
        binding = HouseholdBinding.model_validate(data["binding"])
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
            other = run(Scenario.model_validate_json(alternative), batch, binding, indices)
            comparison = dict(result=other, differences=paired(result, other))
        st.session_state.update(
            market_household_result=dict(
                baseline=result, comparison=comparison, batch=batch.export()
            ),
            market_household_input=edited,
        )
    except (ValueError, KeyError, TypeError) as error:
        invalid(error, "market_household")
