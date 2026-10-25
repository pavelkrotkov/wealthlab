"""Editable actual policy-event audit with conditional federal and independent NJ tax."""

import streamlit as st

from wealthlab.products.life_contract import run
from wealthlab.products.life_contract_example import synthetic
from wealthlab.products.life_contract_inputs import LifeContractCase
from wealthlab.ui.life_contract_results import display
from wealthlab.ui.uploads import invalid, source

NAMESPACE = "life_contract"


def show():
    st.subheader("Whole-life contract cash and taxes")
    st.warning(
        "Conditional personal-policy profile. Events on this page are supplied as executed "
        "and fully funded; household premium funding and liquid-saving/protection comparison "
        "remain separate work. Insurer values, MEC status and tax eligibility are assumptions."
    )
    st.caption(
        "Surrender/lapse amount is total settlement BEFORE loan repayment; only the remainder "
        "is cash. Capitalized interest increases debt without cash. MEC income-first amounts "
        "need pre-event cash value BEFORE surrender charges. Supplied NJ ordinary income is "
        "independent and enters Other income, without pension exclusion. Null recognition "
        "blocks annual tax conclusions. No automatic lapse, seven-pay test, contract changes, "
        "aggregated MECs, deductible loan interest or tax-payment timing is inferred."
    )
    uploaded = st.file_uploader("Load whole-life contract JSON", type="json")
    if source(uploaded, synthetic().model_dump_json(indent=2), NAMESPACE) is None:
        return
    with st.form(NAMESPACE):
        edited = st.text_area(
            "Executed policy events, contract assumptions and annual baselines (JSON)",
            key=f"{NAMESPACE}_editor",
            height=400,
        )
        submitted = st.form_submit_button("Audit policy cash and taxes", type="primary")
    if submitted:
        calculate(edited)
    if f"{NAMESPACE}_result" in st.session_state:
        display(st.session_state[f"{NAMESPACE}_result"])


def calculate(edited):
    try:
        result = run(LifeContractCase.model_validate_json(edited))
        st.session_state.update(life_contract_result=result, life_contract_input=edited)
    except (ValueError, TypeError) as error:
        invalid(error, NAMESPACE)
