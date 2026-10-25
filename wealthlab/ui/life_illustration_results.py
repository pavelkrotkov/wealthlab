"""Separate living value, protection, debt and dated returns for supplied paths."""

import json

import pandas as pd
import streamlit as st

from wealthlab.products.life_illustration_csv import export
from wealthlab.products.life_illustration_inputs import LifeStudy

IRRS = ("cash_value_irr", "surrender_irr", "death_irr")


def display(result):
    st.subheader("Supplied policy values and dated returns")
    st.caption(
        "All returns are before tax. Cash-value, surrender and death returns are separate "
        "terminal alternatives; death benefit is not added to cash value. Loan proceeds are "
        "offset by debt, including supplied capitalized interest. A dividend interest rate "
        "is not a policy IRR. Null means unknown or no unique conventional IRR, never zero."
    )
    st.dataframe(pd.DataFrame([summary(case) for case in result["illustrations"]]), hide_index=True)
    labels = {case["id"]: case["name"] for case in result["illustrations"]}
    selected = st.selectbox("Illustration detail", labels, format_func=lambda value: labels[value])
    case = next(case for case in result["illustrations"] if case["id"] == selected)
    rows = pd.DataFrame([flatten(row) for row in case["rows"]])
    st.dataframe(rows, hide_index=True, width="stretch")
    chart = rows.set_index("date")[["net_cash_value", "net_surrender_value", "net_death_benefit"]]
    st.line_chart(chart.astype(float))
    st.dataframe(pd.DataFrame(case["dated_cash"]), hide_index=True)
    with st.expander("Source metadata, assumptions and full audit"):
        st.json(result)
    downloads(result)


def summary(case):
    return dict(
        illustration=case["name"],
        scale=case["scale"],
        premium_paid=case["totals"]["premium"],
        premiums_from_retirement=case["premiums_from_retirement"],
        terminal_surrender_value=case["rows"][-1]["net_surrender_value"],
        terminal_death_benefit=case["rows"][-1]["net_death_benefit"],
        protection_shortfall=case["rows"][-1]["protection_shortfall"],
    )


def flatten(row):
    plain = {key: value for key, value in row.items() if key not in IRRS}
    for key in IRRS:
        plain[key] = row[key]["rate"]
        plain[f"{key}_status"] = row[key]["status"]
    return plain


def downloads(result):
    st.download_button(
        "Export policy illustration audit",
        json.dumps(result, default=str),
        "life-illustration-audit.json",
        "application/json",
    )
    st.download_button(
        "Export policy illustration inputs",
        json.dumps(result["inputs"], indent=2),
        "life-illustration-inputs.json",
        "application/json",
    )
    study = LifeStudy.model_validate(result["inputs"])
    st.download_button(
        "Export policy schedules CSV", export(study), "life-illustration-schedules.csv", "text/csv"
    )
