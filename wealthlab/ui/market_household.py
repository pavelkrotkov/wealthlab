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
from wealthlab.markets.inputs import MarketCase
from wealthlab.markets.paths import generate
from wealthlab.markets.policy_example import CHOICES
from wealthlab.markets.policy_example import enable as policy_example
from wealthlab.markets.stresses import NAMES
from wealthlab.markets.workplace_example import synthetic as workplace_example
from wealthlab.markets.wrapper_example import synthetic as wrapper_example
from wealthlab.ui.market_household_results import display
from wealthlab.ui.uploads import invalid, source


def show():
    st.subheader("Actual household market funding")
    st.caption(
        "Month-end prices fund spending through actual taxable lots and the same tax return. "
        "Opening holdings receive separately taxed cash yield; selected expenses use prior "
        "realized CPI. Other accounts retain their explicit entered schedules. The synthetic "
        "two-year horizon does not cover retirement through age 100. Dated staged/target sales "
        "and conditional harvesting use current marks. Explicit IRA/529 proxies and employer "
        "net factors reuse their ledgers; linked employment reacts next month. "
        "Broader rebalancing remains unfinished. "
        "Optional discretionary guardrails use observed real wealth; "
        "their cuts are reported separately."
    )
    mode = st.selectbox(
        "Household market mode", ["deterministic", "monte_carlo", "historical", "stress"]
    )
    stress = st.selectbox("Household named stress", NAMES)
    household, market, binding = account_example(mode, stress)
    if st.checkbox("Use synthetic discretionary guardrail", key="market_guardrail_example"):
        household, binding = enable(household, binding)
    if household.lot_plan is not None:
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
        alternative = st.text_area("Optional paired household policy (JSON)", value="", height=120)
        st.caption(
            "The alternative accepts household JSON or {household, binding} to compare "
            "employment triggers or other binding policies on the same realized market batch."
        )
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
        ["Taxable lots", "IRA and education proxies", "Employer and employment", "Employee 401(k)"],
        key="market_account_scope",
    )
    starter = {
        "Taxable lots": synthetic,
        "IRA and education proxies": wrapper_example,
        "Employer and employment": employer_example,
        "Employee 401(k)": workplace_example,
    }[scope]
    return starter(mode, stress)
