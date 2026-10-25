"""Editable annual tax cases with explicit jurisdiction inputs and payment balances."""

import json

import streamlit as st

from wealthlab.tax.annual import AnnualCase, evaluate, synthetic
from wealthlab.ui.tax_results import display

SECTIONS = {
    "Filing and policy": ["filing", "policy"],
    "Federal income and deductions": ["federal_income", "federal_deductions"],
    "New Jersey income and deductions": ["nj_income", "nj_deductions"],
    "Tax payments already made": ["payments"],
}


def table(values: dict, key: str) -> dict:
    """Native table handles scalar fields; nested records use labelled JSON below."""
    scalars = [
        {"field": name, "value": str(value).lower() if isinstance(value, bool) else str(value)}
        for name, value in values.items()
        if not isinstance(value, (dict, list))
    ]
    edited = st.data_editor(scalars, key=key, disabled=["field"], hide_index=True, width="stretch")
    result = {row["field"]: row["value"] for row in edited}
    for name, value in values.items():
        if isinstance(value, (dict, list)):
            result[name] = st.text_area(
                name.replace("_", " ").title(), json.dumps(value, indent=2), key=f"{key}_{name}"
            )
    return result


def form(case: AnnualCase) -> AnnualCase | None:
    data = case.model_dump(mode="json")
    with st.form("annual_tax_case"):
        for title, fields in SECTIONS.items():
            with st.expander(title, expanded=title.startswith("Filing")):
                for name in fields:
                    st.caption(name.replace("_", " ").title())
                    data[name] = table(data[name], f"tax_{name}")
        data["nj_filing"] = st.text_area(
            "NJ filing override (JSON; null inherits federal filing)",
            json.dumps(data.get("nj_filing"), indent=2),
        )
        data["nj_regime"] = st.selectbox(
            "NJ rule regime",
            ["published_2025", "freeze_2025"],
            index=int(case.nj_regime == "freeze_2025"),
        )
        submitted = st.form_submit_button("Calculate annual taxes", type="primary")
    return parse(data, case) if submitted else None


def show():
    st.header("Annual tax workbench")
    st.warning(
        "Synthetic starting case. NJ currently supports full-year resident income-tax core; "
        "other-state, child, earned-income and care credits and special assessments are excluded. "
        "This screen is not yet connected to monthly household funding."
    )
    st.caption(
        "All money is annual USD. Federal and NJ amounts use their own "
        "recognized income and basis. "
        "Qualified dividends are included in total dividends; collections are JSON. "
        "Ordinary noninvestment income is a supplied positive classification, excluding "
        "wages, investments, retirement and business income; no eligibility is inferred. "
        "Insurance ordinary income is supplied recognized policy income subject to NIIT; "
        "insurance additional tax is an entered liability, without inferred MEC eligibility. "
        "Positive balances are due, negative balances are overpayments. No payment is sent."
    )
    try:
        case = st.session_state.setdefault("annual_case", synthetic())
        updated = form(case)
        if updated is not None:
            result = evaluate(updated)
            st.session_state.update(annual_case=updated, annual_result=result)
            case = updated
        result = st.session_state.get("annual_result")
        if result is not None:
            display(case, result)
    except (ValueError, OSError) as error:
        st.error(str(error))


def parse(data: dict, case: AnnualCase) -> AnnualCase:
    """Parse nested JSON only after submission so malformed text remains editable.

    Rendering must finish the form, including its submit button, before validation
    can fail. Otherwise an invalid dependent or carry list would trap the user.
    """
    for section, original in case.model_dump(mode="json").items():
        if section == "nj_filing":
            data[section] = json.loads(data[section])
        elif isinstance(original, dict):
            for name, value in original.items():
                if isinstance(value, (dict, list)):
                    data[section][name] = json.loads(data[section][name])
    return AnnualCase.model_validate(data)
