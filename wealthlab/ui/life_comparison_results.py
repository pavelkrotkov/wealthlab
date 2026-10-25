"""Keep spending, protection and recognized taxes beside each wealth comparison."""

import json

import pandas as pd
import streamlit as st


def display(result):
    st.subheader("Matched household funding and insurance alternatives")
    st.warning(
        "Marked living wealth deducts recognized tax; future unexecuted exit taxes are excluded. "
        "Death protection is shown separately. A wealth advantage does not establish spending "
        "safety, sufficient insurance or equivalent risk. Supplied policy paths are conditional, "
        "and the synthetic three-month examples do not establish retirement funding success."
    )
    outcomes = [
        dict(alternative=name, **row)
        for name, value in result["alternatives"].items()
        for row in value["outcomes"]
    ]
    frame = pd.DataFrame(outcomes)
    st.dataframe(
        frame[
            [
                "alternative",
                "path",
                "funding_failure_months",
                "reserve_breach_months",
                "maximum_protection_gap",
                "premiums_from_retirement",
                "future_retirement_premiums",
            ]
        ],
        hide_index=True,
    )
    st.dataframe(
        frame.drop(columns=["partial_tax_years", "provisional_tax_years"]), hide_index=True
    )
    st.caption(
        "Each path number uses the same realized market observations across alternatives. "
        "Unfilled optional saving is separate from unpaid required premiums and bills."
    )
    with st.expander("Matched inputs, realized paths, trades, policy events and tax audit"):
        st.json(result)
    scenario_exports(result)
    st.download_button(
        "Export insurance comparison inputs",
        json.dumps(result["inputs"], indent=2),
        "insurance-comparison-inputs.json",
        "application/json",
    )
    st.download_button(
        "Export insurance comparison audit",
        json.dumps(result, default=str),
        "insurance-comparison-audit.json",
        "application/json",
    )
    st.download_button(
        "Export comparison outcomes",
        frame.to_csv(index=False),
        "insurance-comparison-outcomes.csv",
        "text/csv",
    )


def scenario_exports(result):
    with st.expander("Open an individual alternative in Household"):
        st.caption(
            "Download a scenario below, then import its JSON in Household to edit it separately."
        )
        for index, (name, scenario) in enumerate(result["inputs"]["alternatives"].items()):
            st.download_button(
                f"Export {name} household",
                json.dumps(scenario, indent=2),
                f"insurance-household-{index}.json",
                "application/json",
            )
